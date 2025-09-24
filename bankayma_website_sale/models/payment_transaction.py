# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        if not self.invoice_ids and self.sale_order_ids.website_id:
            result["DocumentType"] = "8"
        return result
