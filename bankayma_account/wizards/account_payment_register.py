# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    comment = fields.Text()
    use_sumit_journal = fields.Boolean()
    use_sumit_this_payment = fields.Boolean(string="Push to sumit")

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        result["use_sumit_journal"] = (
            self.env["account.move.line"]
            .browse(result.get("line_ids", [(False, False, [])])[0][2])
            .mapped("move_id.journal_id.use_sumit")[0]
        )
        if "use_sumit_this_payment" not in result:
            result["use_sumit_this_payment"] = result["use_sumit_journal"]
        return result

    def _create_payments(self):
        """Create invoice from parent company for paid invoices"""
        for journal in self.line_ids.mapped("move_id.journal_id"):
            journal.read(["use_sumit"])
            journal._cache["use_sumit"] = self.use_sumit_this_payment
        return super()._create_payments()

    def _create_payment_vals_from_wizard(self, batch_result):
        result = super()._create_payment_vals_from_wizard(batch_result)
        if self.comment:
            result["bankayma_comment"] = self.comment
        return result

    def _create_payment_vals_from_batch(self, batch_result):
        result = super()._create_payment_vals_from_batch(batch_result)
        if self.comment:
            result["bankayma_comment"] = self.comment
        return result
