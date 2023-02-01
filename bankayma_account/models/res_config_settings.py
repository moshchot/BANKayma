# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    intercompany_sale_journal_id = fields.Many2one(
        related="company_id.intercompany_sale_journal_id", readonly=False
    )
    intercompany_purchase_journal_id = fields.Many2one(
        related="company_id.intercompany_purchase_journal_id", readonly=False
    )
