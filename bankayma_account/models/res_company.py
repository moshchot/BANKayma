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

    name = fields.Char(translate=True)
    company_cascade_from_parent = fields.Boolean("Cascade from parent")
    intercompany_sale_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany sale journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "sale")],
    )
    intercompany_purchase_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany purchase journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "purchase")],
    )

    def _company_cascade_get_companies(self):
        return self.mapped("child_ids").filtered("company_cascade_from_parent")

    def _company_cascade_create(self, values):
        """Never cascade creating"""
        return self.browse([])

    def _company_cascade_write(self, values):
        """Never cascade writing"""
        return self.browse([])
