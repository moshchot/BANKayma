# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_payment_term_id = fields.Many2one(
        domain=lambda self: self._domain_invoice_payment_term_id()
    )

    def _domain_invoice_payment_term_id(self):
        """Generate group specific domain for invoice_payment_term_id"""
        return (
            "['|', ('fixed_date', '=', False), ('fixed_date', '>', current_date)]"
            if not self.env.user.has_group("bankayma_base.group_org_manager")
            else "[]"
        )

    def _bankayma_invoice_child_income_get_parent_company(self):
        """Get the parent that invoices overhead"""
        company = self.company_id.parent_id
        while company.parent_id:
            company = company.parent_id
        return company
