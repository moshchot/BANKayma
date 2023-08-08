# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")
    bankayma_vendor_tax_percentage = fields.Float()
    bankayma_vendor_max_amount = fields.Float()
