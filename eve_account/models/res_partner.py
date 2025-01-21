# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    eve_vendor_code = fields.Char("Vendor Internal #")
    eve_customer_code = fields.Char("Customer #")
