# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    plan_id = fields.Many2one(default=lambda self: self._default_analytic_plan_id())
    balance = fields.Monetary(
        groups="account.group_account_readonly,bankayma_base.group_user,"
        "bankayma_base.group_org_manager"
    )

    def _default_analytic_plan_id(self):
        return self.env["account.analytic.plan"].search(
            [
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
