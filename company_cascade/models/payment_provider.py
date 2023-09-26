# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentProvider(models.Model):
    _inherit = ["payment.provider", "company.cascade.mixin"]
    _name = "payment.provider"
