# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class CompanyCascadeUpMixin(models.AbstractModel):
    _name = "company.cascade.up.mixin"
    _description = "Cascade values upwards"
    _company_cascade_up_create = True
    _company_cascade_up_write = True
    _company_cascade_up_unlink = True
    _company_cascade_cascade_create = True
    _company_cascade_cascade_unlink = True
    _company_cascade_cascade_write = True

    @api.model_create_multi
    def create(self, vals_list):
        """When creating records, take care they are created in all companies"""
        result = super().create(vals_list)
        if self._company_cascade_up_enabled("create"):
            result._company_cascade_up()
        return result

    def write(self, vals):
        """When writing records, take care they are written in all companies"""
        result = super().write(vals)
        if self._company_cascade_up_enabled("write"):
            self._company_cascade_up(vals=vals)
        return result

    def unlink(self):
        """Delete all records when unlinking"""
        all_records = self._company_cascade_get_all()
        result = super().unlink()
        if all_records.exists() and self._company_cascade_up_enabled("unlink"):
            all_records.exists().unlink()
        return result

    def _company_cascade_up_enabled(self, action):
        return (
            not self.env.context.get("install_mode")
            and not self.env.context.get("company_cascade_up")
            and getattr(self, "_company_cascade_up_%s" % action, True)
        )

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

            else:
                parent_company = this.company_id.parent_id
                if parent_company and parent_company != this.company_id:
                    this_vals = this.read(
                        self._company_cascade_field_names_scalar(this._fields),
                        load="_classic_write",
                    )[0]
                    parent_vals = self._company_cascade_values(
                        parent_company,
                        dict(vals or {}, **this_vals),
                    )
                    candidate = (
                        self._company_cascade_find_candidate(
                            parent_company, parent_vals
                        )
                        .with_context(company_cascade_up=True)
                        .with_company(parent_company)
                    )
                    if candidate:
                        if vals:
                            candidate.write(
                                {k: v for k, v in parent_vals.items() if k in vals}
                            )
                        this.with_context(
                            company_cascade_up=False, company_cascade=False
                        ).company_cascade_parent_id = candidate
                    else:
                        self.create(parent_vals)
