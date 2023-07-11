# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrSequence(models.Model):
    _inherit = ["ir.sequence", "company.cascade.mixin"]
    _name = "ir.sequence"
