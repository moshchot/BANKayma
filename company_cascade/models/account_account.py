# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAccount(models.Model):
    _inherit = ["account.account", "company.cascade.mixin"]
    _name = "account.account"
    _company_cascade_force_fields = ("account_type",)
