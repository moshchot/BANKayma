# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticAccount(models.Model):
    _inherit = ["account.analytic.account", "company.cascade.mixin"]
    _name = "account.analytic.account"
