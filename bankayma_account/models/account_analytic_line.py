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
    bankayma_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        compute="_compute_bankayma_analytic_account_id",
        store=True,
    )
    operating_unit_id = fields.Many2one(related="move_line_id.operating_unit_id")
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
                "bankayma_balance": this.amount,
            }
            journal = this.move_line_id.journal_id
            if (
                journal.intercompany_sale_company_id
                or journal.intercompany_purchase_company_id
            ):
                vals["bankayma_type"] = "intercompany"
                vals["bankayma_intercompany"] = this.amount
            elif this.amount < 0:
                vals["bankayma_type"] = "expense"
                vals["bankayma_expense"] = this.amount
            else:
                vals["bankayma_type"] = "income"
                vals["bankayma_income"] = this.amount
            this.update(vals)

    @api.depends(lambda self: self._get_plan_fnames())
    def _compute_bankayma_analytic_account_id(self):
        for this in self:
            this.bankayma_analytic_account_id = this._get_analytic_accounts()[:1].id

    def action_open_move(self):
        return {
            "name": self.move_line_id.move_id.display_name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "views": [(False, "form")],
            "res_model": self.move_line_id.move_id._name,
            "res_id": self.move_line_id.move_id.id,
            "target": "current",
        }
