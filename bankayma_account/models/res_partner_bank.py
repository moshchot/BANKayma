# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    branch_code = fields.Char(pattern="[0-9]+")
    acc_number = fields.Char(pattern="[0-9]+")
