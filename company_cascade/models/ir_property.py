# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import threading

from odoo import api, models


class IrProperty(models.Model):
    _inherit = ["ir.property", "company.cascade.mixin"]
    _name = "ir.property"
    _company_cascade_cascade_create = True
    _company_cascade_cascade_write = True

    @api.model_create_multi
    def create(self, vals_list):
        """When creating properties, take care they are created in all companies"""
        result = super().create(vals_list)
        if not self.env.context.get("company_cascade_up"):
            result._company_cascade_up()
        return result

    def write(self, vals):
        """When writing properties, take care they are written in all companies"""
        result = super().write(vals)
        if not self.env.context.get("company_cascade_up"):
            self._company_cascade_up(vals=vals)
        return result

    def unlink(self):
        """Delete all properties when unlinking"""
        all_records = self._company_cascade_get_all()
        result = super().unlink()
        if all_records.exists():
            all_records.exists().unlink()
        return result

    @api.model
    def _set_multi(self, name, model, values, default_value=None):
        """Intercept sql delete"""
        thread = threading.current_thread()
        hooks = list(getattr(thread, "query_hooks", []))
        thread.query_hooks = hooks

        to_delete_ids = []

        def intercept_delete(cursor, query, params, start, delay):
            if query.startswith("DELETE FROM ir_property WHERE id="):
                to_delete_ids.extend(params)

        hooks.append(intercept_delete)

        result = super()._set_multi(name, model, values, default_value=default_value)

        thread.query_hooks = tuple(hook for hook in hooks if hook != intercept_delete)

        if to_delete_ids:
            self.browse(to_delete_ids).unlink()

        return result

    def _company_cascade_up(self, vals=None):
        """Cascade changes upwards"""
        for this in self:
            parent = this
            while parent.company_cascade_parent_id:
                parent = parent.company_cascade_parent_id
            if parent and parent != this:
                parent_vals = (
                    vals
                    and self._company_cascade_values(parent.company_id, vals)
                    or None
                )
                if parent_vals:
                    parent.with_context(company_cascade_up=True).write(parent_vals)
                parent.with_context(company_cascade_up=True)._company_cascade(
                    fields=parent_vals
                )
            else:
                parent_company = this.company_id
                while parent_company.parent_id:
                    parent_company = parent_company.parent_id
                if parent_company and parent_company != this.company_id:
                    this_vals = this.read(this._fields, load="_classic_write")[0]
                    parent_vals = self._company_cascade_values(
                        parent_company,
                        vals or this_vals,
                    )
                    candidate = (
                        self._company_cascade_find_candidate(
                            parent_company, parent_vals
                        )
                        .with_context(company_cascade_up=True)
                        .with_company(parent_company)
                    )
                    if candidate:
                        candidate.write(
                            self._company_cascade_values(
                                parent_company, vals or this_vals
                            )
                        )
                    else:
                        candidate.create(
                            self._company_cascade_values(parent_company, this_vals)
                        )

    def _company_cascade_values(self, company, vals):
        """Special treatment for value_reference"""
        result = super()._company_cascade_values(company, vals)
        if "value_reference" in result and result["value_reference"]:
            result["value_reference"] = self._company_cascade_value_reference(
                company, None, self.get_by_record()
            )
        return result

    def _company_cascade_find_candidate(self, company, vals):
        return self.search(
            [
                ("fields_id", "=", vals.get("fields_id")),
                ("res_id", "=", vals.get("res_id")),
                ("company_id", "=", company.id),
            ]
        )
