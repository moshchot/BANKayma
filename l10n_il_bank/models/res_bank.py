# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    name = fields.Char(translate=True)
    bank_code = fields.Char()
