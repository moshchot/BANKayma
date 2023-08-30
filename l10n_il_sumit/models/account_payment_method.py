# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .sumit_account import SUMIT_PAYMENT_TYPE_SELECTION


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    sumit_type = fields.Selection(SUMIT_PAYMENT_TYPE_SELECTION, default="1")
