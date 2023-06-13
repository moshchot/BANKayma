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
