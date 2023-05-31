# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = ["account.tax", "company.cascade.mixin"]
    _name = "account.tax"


class AccountTaxRepartitionLine(models.Model):
    _inherit = ["account.tax.repartition.line", "company.cascade.mixin"]
    _name = "account.tax.repartition.line"
