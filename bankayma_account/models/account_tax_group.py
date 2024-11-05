# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    tax_ids = fields.One2many("account.tax", "tax_group_id")
    bankayma_offer_removal = fields.Boolean(
        "Offer removal",
        help="If this is checked, moves with taxes belonging to this group offer a "
        "button to remove all those taxes",
    )
