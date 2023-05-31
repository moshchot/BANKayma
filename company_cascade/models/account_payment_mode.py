# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentMode(models.Model):
    _inherit = ["account.payment.mode", "company.cascade.mixin"]
    _name = "account.payment.mode"
