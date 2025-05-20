# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models
from odoo.fields import Command
from odoo.tools import frozendict

from odoo.addons.account_move_update_analytic.models.account_move_line import (
    force_state_sentinel,
)


class AccountMoveUpdateAnalytic(models.TransientModel):
    _inherit = "account.move.update.analytic.wizard"

    def update_analytic_lines(self):
        # super will recompute taxes, so we need to save the balances of
        # potentially changed taxes and impose those values after the tax
        # recomputation happened. as the original tax line(s) have been
        # deleted, we need to match the new tax line by tax key, but without
        # considering the analytic distribution as we're about to change that

        move = self.line_id.move_id

        def tax_key(line):
            return frozendict(line.tax_key, analytic_distribution=False)

        custom_taxes_wizard = (
            self.env["bankayma.move.edit.tax.totals"]
            .with_context(
                active_ids=move.ids,
            )
            .sudo()
            .create({})
        )
        taxkey2balance = {
            tax_key(line.line_id): line.balance for line in custom_taxes_wizard.line_ids
        }
        ml2balance = {line: line.balance for line in move.line_ids}

        if move.state == "posted":
            for line in move.line_ids:
                if any(
                    line2
                    for line2 in move.line_ids
                    if line2 != line and tax_key(line) == tax_key(line2)
                ):
                    raise exceptions.UserError(
                        _(
                            "This move is too complex for inline changing. "
                            "Revert it and edit a copy"
                        )
                    )

        result = super().update_analytic_lines()

        changed_move_lines = [
            Command.update(line.id, {"balance": balance})
            for line, balance in ml2balance.items()
            if line.exists()
        ] + [
            Command.update(line.id, {"balance": taxkey2balance[tax_key(line)]})
            for line in move.line_ids
            if tax_key(line) in taxkey2balance
        ]

        if changed_move_lines:
            move.with_context(
                check_move_validity=False,
                account_move_update_analytic=force_state_sentinel,
            ).write(
                {
                    "line_ids": changed_move_lines,
                }
            )
            move.line_ids.analytic_line_ids.unlink()
            move.line_ids._create_analytic_lines()

        return result
