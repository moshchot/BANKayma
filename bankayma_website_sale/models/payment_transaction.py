# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _to_sumit_vals(self):
        """Set sumit document type to 8 (order) for orders"""
        result = super()._to_sumit_vals()
        if not self.invoice_ids and self.sale_order_ids.website_id:
            result["DocumentType"] = "8"
            if self.provider_id.journal_id.bankayma_mail_template_invoice_paid:
                result["SendUpdateByEmailAddress"] = False
        return result
