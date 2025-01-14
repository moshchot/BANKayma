# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .account_move import VALIDATED_STATE_SELECTION


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    validated_state = fields.Selection(VALIDATED_STATE_SELECTION)
    bankayma_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic account",
    )
    bankayma_analytic_plan_id = fields.Many2one(
        "account.analytic.plan",
        string="Analytic plan",
    )
    bankayma_payment_date = fields.Date("Payment Date")

    @api.model
    def _select(self):
        return (
            super()._select() + ", validated_state, bankayma_analytic_account_id, "
            "bankayma_analytic_plan_id, bankayma_payment_date"
        )
