# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ["res.company", "company.cascade.mixin"]
    _name = "res.company"
    _company_cascade_exclude_fields = (
        "account_opening_move_id",
        "bank_account_code_prefix",
        "bank_journal_ids",
        "child_ids",
        "cash_account_code_prefix",
        "code",
        "company_cascade_from_parent",
        "name",
        "partner_id",
        "parent_id",
        "user_ids",
    )

    company_cascade_from_parent = fields.Boolean("Cascade from parent")
    company_id = fields.Many2one(
        "res.company",
        compute=lambda self: [this.update({"company_id": this}) for this in self],
    )

    def write(self, vals):
        result = super().write(vals)
        if "parent_id" in vals:
            for this in self.filtered("company_cascade_from_parent"):
                this._company_cascade_fix_hierarchy()
        return result

    def _company_cascade_get_companies(self):
        """To fit into the cascading mechanism, companies pretend to be their own company"""
        return self.mapped("child_ids").filtered("company_cascade_from_parent")

    def _company_cascade_get_children(self):
        """To fit into the cascading mechanism, companies pretend to be their own company"""
        return self._company_cascade_get_companies()

    def _company_cascade(self, fields=None):
        """Only cascade explicitly requested fields"""
        if fields:
            return super()._company_cascade(fields=fields)

    def _company_cascade_fix_hierarchy(self):
        """When moving a company in the hierarchy tree, we need to fix cascading parents"""
        for model in self.env["company.cascade.mixin"]._inherit_children:
            for record in self.env[model].search(
                [
                    ("company_cascade_parent_id", "!=", False),
                    ("company_id", "in", self.ids),
                ]
            ):
                if (
                    record.company_cascade_parent_id.company_id
                    != record.company_id.parent_id
                ):
                    record.company_cascade_parent_id = (
                        record._company_cascade_get_all(record.company_id.parent_id)
                        if record.company_id.parent_id
                        else False
                    )
