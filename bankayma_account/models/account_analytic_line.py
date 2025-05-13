# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    bankayma_type = fields.Selection(
        [
            ("expense", "Expense"),
            ("income", "Income"),
            ("intercompany", "Intercompany"),
        ],
        "Type",
        compute="_compute_bankayma_fields",
        store=True,
        compute_sudo=True,
    )
    bankayma_income = fields.Monetary(
        "Income", compute="_compute_bankayma_fields", store=True, compute_sudo=True
    )
    bankayma_expense = fields.Monetary(
        "Expense", compute="_compute_bankayma_fields", store=True, compute_sudo=True
    )
    bankayma_intercompany = fields.Monetary(
        "Intercompany",
        compute="_compute_bankayma_fields",
        store=True,
        compute_sudo=True,
    )
    bankayma_balance = fields.Monetary(
        "Balance", compute="_compute_bankayma_fields", store=True, compute_sudo=True
    )
    move_id = fields.Many2one(related="move_line_id.move_id")
    fiscal_position_id = fields.Many2one(
        related="move_line_id.move_id.fiscal_position_id"
    )

    @api.depends("amount", "currency_id")
    def _compute_bankayma_fields(self):
        for this in self:
            vals = {
                "bankayma_income": 0,
                "bankayma_expense": 0,
                "bankayma_intercompany": 0,
                "bankayma_balance": 0,
            }
            journal = this.move_line_id.journal_id
            if (
                journal.intercompany_sale_company_id
                or journal.intercompany_purchase_company_id
            ):
                vals["bankayma_type"] = "intercompany"
                vals["bankayma_intercompany"] = this.amount
                vals["bankayma_balance"] = this.amount
            elif this.amount < 0:
                vals["bankayma_type"] = "expense"
                vals["bankayma_expense"] = -this.amount
                vals["bankayma_balance"] = this.amount
            else:
                vals["bankayma_type"] = "income"
                vals["bankayma_income"] = this.amount
                vals["bankayma_balance"] = this.amount
            this.update(vals)
