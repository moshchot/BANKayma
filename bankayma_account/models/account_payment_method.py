# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    @api.model
    def _get_payment_method_information(self):
        """Add fake summit_* payment methods to identify payments"""
        result = super()._get_payment_method_information()
        method_def = {"mode": "multi", "domain": [("type", "in", ("bank", "cash"))]}
        result.update(
            sumit_bank=method_def,
            sumit_cheque=method_def,
            sumit_cash=method_def,
            sumit_defrayal=method_def,
            sumit_paypal=method_def,
            sumit_masav=method_def,
            sumit_other=method_def,
        )
        return result
