# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.fields import Command

from odoo.addons.account_move_update_analytic.models.account_move_line import (
    force_state_sentinel,
)


class AccountMoveUpdateAnalytic(models.TransientModel):
    _inherit = "account.move.update.analytic.wizard"

    def update_analytic_lines(self):
        custom_taxes_wizard = (
            self.env["bankayma.move.edit.tax.totals"]
            .with_context(
                active_ids=self.line_id.move_id.ids,
                account_move_update_analytic=force_state_sentinel,
            )
            .sudo()
            .create({})
        )
        tax2amount = {
            line.line_id.tax_line_id: line.balance
            for line in custom_taxes_wizard.line_ids
        }
        custom_taxes_wizard.line_ids = False

        result = super().update_analytic_lines()

        custom_taxes_wizard.line_ids = [
            Command.create(
                {
                    "line_id": self.line_id.move_id.line_ids.filtered(
                        lambda x: x.tax_line_id == tax
                    )[:1].id,
                    "balance": balance,
                }
            )
            for tax, balance in tax2amount.items()
            if tax in self.line_id.move_id.line_ids.tax_line_id
        ]

        custom_taxes_wizard.action_edit_tax_totals()

        return result
