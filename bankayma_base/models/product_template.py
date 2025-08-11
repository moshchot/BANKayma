# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        default=lambda self: self.env.user._get_default_operating_unit(),
    )
