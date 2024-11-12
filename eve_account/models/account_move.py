# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _bankayma_invoice_child_income(
        self,
        fraction=0.07,
        post=True,
        pay=True,
    ):
        return super()._bankayma_invoice_child_income(
            fraction=self.journal_id.bankayma_overhead_percentage / 100,
            post=post,
            pay=pay,
        )
