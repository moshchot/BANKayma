# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPositionTaxDeduction(models.Model):
    _name = "account.fiscal.position.tax.deduction"
    _description = "Tax decution for fiscal position"
    _rec_name = "amount"
    _order = "amount asc"

    fiscal_position_id = fields.Many2one("account.fiscal.position", required=True)
    deduction_percentpoints = fields.Float(required=True, string="Deduction %")
    amount = fields.Float(required=True)
