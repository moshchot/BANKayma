# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("sumit", "Sumit")], ondelete={"sumit": "cascade"}
    )
    sumit_account_id = fields.Many2one("sumit.account", required_if_provider="sumit")
    sumit_installment_threshold = fields.Monetary(
        "Threshold for installments",
        currency_field="main_currency_id",
        help="If a transaction amount is above this value, it may be paid in installments",
    )
    sumit_installment_count = fields.Integer(
        "Maximum installments", help="The maximum amount of installments to allow"
    )

    def _should_build_inline_form(self, is_validation=False):
        if self.code == "sumit":
            return False
        else:
            return super()._should_build_inline_form(is_validation=is_validation)
