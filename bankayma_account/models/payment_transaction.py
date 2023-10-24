# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    is_recurrent = fields.Boolean()

    def _process_notification_data(self, notification_data):
        """Coerce current company to provider's company for further processing"""
        return super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._process_notification_data(notification_data)

    def _finalize_post_processing(self):
        """Coerce current company to provider's company for further processing"""
        return super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._finalize_post_processing()
