# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccounFiscalPosition(models.Model):
    _inherit = ["account.fiscal.position", "company.cascade.mixin"]
    _name = "account.fiscal.position"


class AccounFiscalPositionTax(models.Model):
    _inherit = ["account.fiscal.position.tax", "company.cascade.mixin"]
    _name = "account.fiscal.position.tax"
