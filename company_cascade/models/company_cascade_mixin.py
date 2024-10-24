# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections.abc import Iterable
from contextlib import contextmanager

from odoo import api, fields, models


class CompanyCascadeMixin(models.AbstractModel):
    _name = "company.cascade.mixin"
    _description = "Cascade values to child companies"
    _company_cascade_exclude_fields = tuple([])
    _company_cascade_force_fields = tuple([])
    _company_cascade_cascade_create = False
    _company_cascade_cascade_unlink = False
    _company_cascade_cascade_write = False

    company_cascade_parent_id = fields.Many2one(
        "unknown",
        auto_join=True,
        ondelete="cascade",
        copy=False,
    )
    company_cascade_child_ids = fields.One2many(
        inverse_name="company_cascade_parent_id", auto_join=True
    )

    @api.model
    def _setup_fields(self):
        self._fields["company_cascade_parent_id"].comodel_name = self._name
        self._fields["company_cascade_child_ids"].comodel_name = self._name
        return super()._setup_fields()

    # todo constraints
    # self.company_cascade_parent_id.company_id == self.company_id.parent_id
    # unique(company_id, company_cascade_parent_id)

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        if self._company_cascade_cascade_create and self.env.context.get(
            "company_cascade", True
        ):
            for this, vals in zip(result, vals_list):
                this._company_cascade_create(vals)
        return result

    def write(self, vals):
        if self.env.context.get("mass_edit"):
            result = True
            for this in self:
                write_vals = self._company_cascade_values(this.company_id, vals)
                result &= this.with_context(mass_edit=None).write(write_vals)
            return result
        result = super().write(vals)
        if self._company_cascade_cascade_write and self.env.context.get(
            "company_cascade", True
        ):
            for this in self:
                this._company_cascade_write(vals)
        return result

    def unlink(self):
        if self._company_cascade_cascade_unlink and self.env.context.get(
            "company_cascade", True
        ):
            self.mapped("company_cascade_child_ids").unlink()
        return super().unlink()

    def _company_cascade(self, fields=None, recursive=False, recursive_seen=None):
        """Overwrite/create equivalent records in child companies"""
        result = self.browse([])
        # TODO: sort by self._company_cascade_order?
        if recursive:
            seen = recursive_seen or []
            for field_name, field in self._fields.items():
                if fields and field_name not in fields or not field.comodel_name:
                    continue
                if "company_cascade_parent_id" not in self.env[
                    field.comodel_name
                ] or field.comodel_name in (self._name, "res.company"):
                    continue
                for this in self:
                    seen.append(this)
                    if this[field_name] in seen or not this[field_name]:
                        continue
                    seen.append(this[field_name])
                    this[field_name]._company_cascade(
                        recursive=True, recursive_seen=seen
                    )
        # first step: exclude x2many fields that cascade themselves
        for this in self:
            if not this.company_id:
                continue
            values = this.read(
                self._company_cascade_field_names_scalar(fields),
                load="_classic_write",
            )[0]
            with self._company_cascade_protect():
                result += this._company_cascade_write(values)
                result += this._company_cascade_create(values)
            for result_record in result:
                this.copy_translations(result_record)

        self.env.flush_all()
        # second step: write x2many fields that cascade themselves
        field_names = self._company_cascade_field_names_cascading(fields)
        if not field_names:
            return result
        for this in self:
            if not this.company_id:
                continue
            values = this.read(field_names, load="_classic_write")[0]
            for field in field_names:
                this[field]._company_cascade()
            with self._company_cascade_protect():
                this._company_cascade_write(values)

        return result

    def _company_cascade_values(self, company, vals):
        """Map values to their equivalent value in company"""
        return {
            key: company.id
            if key == "company_id"
            else val
            if key not in self._fields
            or self._fields[key].comodel_name not in self.env
            or "company_cascade_parent_id"
            not in self.env[self._fields[key].comodel_name]._fields
            else self._company_cascade_value(company, self._fields[key], val)
            for key, val in vals.items()
            if key
            not in (
                "company_cascade_parent_id",
                "company_cascade_child_ids",
                "message_main_attachment_id",
                "website_message_ids",
                "message_ids",
                "message_follower_ids",
                "activity_ids",
            )
            + self._company_cascade_exclude_fields
            + tuple(models.MAGIC_COLUMNS)
        }

    def _company_cascade_value(self, company, field, value):
        """Map value of field to its equivalent value in company"""
        if not value:
            return value
        if field.type == "many2one":
            return self._company_cascade_value_many2one(company, field, value)
        if field.relational:
            return self._company_cascade_value_x2many(company, field, value)
        if field.type == "reference":
            return self._company_cascade_value_reference(company, field, value)
        return value

    def _company_cascade_value_many2one(self, company, field, value):
        record = self.env[field.comodel_name].browse(value)
        return (
            (record._company_cascade_get_all(company) or record).id
            if record.company_id
            else record.id
        )

    def _company_cascade_value_reference(self, company, field, value):
        if isinstance(value, str):
            record = field.convert_to_record(value, self)
        else:
            record = value
        return "%s,%s" % (
            record._name,
            (
                record
                if "company_cascade_child_ids" not in record._fields
                else record._company_cascade_get_all(company) or record
            ).id,
        )

    def _company_cascade_value_x2many(self, company, field, value):
        return (
            [
                (
                    Command,
                    _id,
                    self.env[field.comodel_name]._company_cascade_values(
                        company, _data
                    ),
                )
                if Command == fields.Command.CREATE
                else (
                    Command,
                    self._company_cascade_value_many2one(company, field, _id),
                    self.env[field.comodel_name]._company_cascade_values(
                        company, _data
                    ),
                )
                if Command == fields.Command.UPDATE
                else (
                    Command,
                    self._company_cascade_value_many2one(company, field, _id),
                    _data,
                )
                if Command
                in (fields.Command.DELETE, fields.Command.UNLINK, fields.Command.LINK)
                else (
                    Command,
                    _id,
                    [
                        self._company_cascade_value_many2one(company, field, __id)
                        for __id in _data
                    ],
                )
                if Command == fields.Command.SET
                else (Command, _id, _data)
                for Command, _id, _data in value
            ]
            if isinstance(value[0], Iterable)
            else [
                self._company_cascade_value_many2one(company, field, _id)
                for _id in value
            ]
        )

    def _company_cascade_get_companies(self):
        return self.sudo().company_id.child_ids.filtered("company_cascade_from_parent")

    def _company_cascade_get_children(self):
        return self.sudo().company_cascade_child_ids

    def _company_cascade_get_all(self, company=None):
        """Return all records that are the equivalent to self in some company"""
        if not self:
            return self.browse([])
        record = self
        while record.company_cascade_parent_id:
            record = record.company_cascade_parent_id
        records = record
        while records.mapped("company_cascade_child_ids") - records:
            records |= records.mapped("company_cascade_child_ids")
        return records.filtered(lambda x: x.company_id == company if company else True)

    def _company_cascade_find_candidate(self, company, vals):
        """
        Find a record in company that's the equivalent of vals.
        This is used before creating cascading record to avoid constraints failing
        """
        if "code" in self._fields and self._fields["code"].required:
            return self.search(
                [
                    ("code", "=", vals.get("code")),
                    "|",
                    ("company_id", "=", company.id),
                    ("company_id", "=", False),
                ],
                order="company_id desc",
            )
        return self.browse([])

    def _company_cascade_create(self, values):
        result = self.browse([])
        create_in_companies = (
            self._company_cascade_get_companies()
            - self._company_cascade_get_children().mapped("company_id")
        )
        for create_in_company in create_in_companies:
            vals = self._company_cascade_values(create_in_company, values)
            vals["company_cascade_parent_id"] = self.id
            candidate = self._company_cascade_find_candidate(create_in_company, vals)
            if candidate:
                vals = {
                    key: value
                    for key, value in vals.items()
                    if not candidate._company_cascade_values_equal(key, value)
                }
                candidate.write(vals)
                result += candidate
            else:
                result += self.sudo().with_company(create_in_company).create(vals)
        return result

    def _company_cascade_write(self, values):
        result = self.browse([])
        for record in self._company_cascade_get_children():
            vals = {
                key: value
                for key, value in self._company_cascade_values(
                    record.company_id, values
                ).items()
                if not record._company_cascade_values_equal(key, value)
            }
            record.sudo().with_company(self.company_id).write(vals)
            result += record
        return result

    def _company_cascade_values_equal(self, field, value):
        """Comare values, return True if value is equal to field's value in self"""
        if self._fields[field].comodel_name:
            return self[field] == self.env[self._fields[field].comodel_name].browse(
                value
            )
        return self[field] == value

    def _company_cascade_field_names_scalar(self, fields=None):
        """
        Return field names that can be just written on child records.
        At first approximation, all stored non-x2x and many2one fields that don't
        cascade themselves
        """
        return [
            field_name
            for field_name, field in self._fields.items()
            if field.store
            and (not field.compute)
            and field_name in (fields or self._fields)
            and field_name not in models.MAGIC_COLUMNS
            and not (
                field.relational
                and field.type != "many2one"
                and "company_cascade_parent_id" in self.env[field.comodel_name]._fields
            )
            or field_name in self._company_cascade_force_fields
        ]

    def _company_cascade_field_names_cascading(self, fields=None):
        """
        Return x2many field names that need to be cascaded, but use models that cascade
        themselves
        """
        return [
            field_name
            for field_name, field in self._fields.items()
            if field.store
            and (not field.compute or not field.inverse)
            and field_name in (fields or self._fields)
            and field_name not in models.MAGIC_COLUMNS + ["company_cascade_child_ids"]
            and (
                field.relational
                and field.type != "many2one"
                and "company_cascade_parent_id" in self.env[field.comodel_name]._fields
            )
        ]

    @contextmanager
    def _company_cascade_protect(self):
        """
        A context manager that disables company checks
        This avoids a lot of unnecessary reads and crashes on recursive computations
        """
        _check_company_org = self.__class__._check_company
        self.__class__._check_company = lambda self, fnames=None: None
        yield
        self.__class__._check_company = _check_company_org
