# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        transactions = self.invoice_line_ids.sale_line_ids.order_id.transaction_ids
        sumit_details = transactions.mapped("sumit_details")
        if any(sumit_details):
            payments = sum(
                map(lambda x: x and x.get("Payments", []) or [], sumit_details), []
            )
            if payments:
                amount = self.amount_total
                for payment in payments:
                    payment["Amount"] = min(payment["Amount"], amount)
                    amount -= payment["Amount"]
                result["Payments"] = payments
        return result
