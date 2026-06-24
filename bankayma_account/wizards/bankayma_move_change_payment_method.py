# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BankaymaMoveChangePaymentMethod(models.TransientModel):
    _name = "bankayma.move.change.payment.method"
    _description = "Change payment method of paid move"

    payment_method_id = fields.Many2one("account.payment.method", required=True)

    def action_change_method(self):
        payments = (
            self.env[self.env.context["active_model"]]
            .browse(self.env.context["active_ids"])
            .mapped(
                "line_ids.full_reconcile_id.reconciled_line_ids.move_id.payment_ids"
            )
        )
        for payment in payments:
            payment.payment_method_line_id = (
                payment.journal_id.inbound_payment_method_line_ids
                + payment.journal_id.outbound_payment_method_line_ids
            ).filtered(lambda x: x.payment_method_id == self.payment_method_id)
