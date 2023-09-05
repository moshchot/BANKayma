# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    tax_ids = fields.One2many("account.tax", "tax_group_id")
