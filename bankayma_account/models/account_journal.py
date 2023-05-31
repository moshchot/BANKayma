# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    bankayma_restrict_intercompany_partner = fields.Boolean(
        "Allow only child companies",
        help="When this checkbox is activated, only child companies of this journals company "
        "may be used as partner on invoices",
    )
    bankayma_restrict_product_ids = fields.Many2many(
        "product.product",
        string="Allowed products",
    )
