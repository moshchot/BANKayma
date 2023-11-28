# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        """Create invoice from parent company for paid invoices"""
        if self.env.user.has_group("bankayma_base.group_org_manager"):
            self = self.with_company(self.mapped("company_id"))
        result = super()._create_payments()
        for move in self.line_ids.mapped("move_id").sudo():
            if move.journal_id.company_cascade_parent_id.bankayma_charge_overhead:
                parent_journal = move.journal_id.company_cascade_parent_id
                move._bankayma_invoice_child_income(
                    fraction=parent_journal.bankayma_overhead_percentage / 100
                )
        return result
