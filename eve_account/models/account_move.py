# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_payment_term_id = fields.Many2one(
        domain="['|', ('fixed_date', '=', False), ('fixed_date', '>', current_date)]"
    )

    def _bankayma_invoice_child_income_get_parent_company(self):
        """Get the parent that invoices overhead"""
        company = self.company_id.parent_id
        while company.parent_id:
            company = company.parent_id
        return company
