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
    overhead_journal_id = fields.Many2one(
        related="company_id.overhead_journal_id", readonly=False
    )
    overhead_account_id = fields.Many2one(
        related="company_id.overhead_account_id", readonly=False
    )
    overhead_payment_journal_id = fields.Many2one(
        related="company_id.overhead_payment_journal_id", readonly=False
    )
    donation_journal_id = fields.Many2one(
        related="company_id.donation_journal_id", readonly=False
    )
    show_bankayma_tax_totals_in_invoice = fields.Boolean(
        string="Show custom tax totals for vendor bills",
        config_parameter="bankayma_show_bankayma_tax_totals_in_invoice",
    )
    show_bankayma_tax_totals_out_invoice = fields.Boolean(
        string="Show custom tax totals for customer invoices",
        config_parameter="bankayma_show_bankayma_tax_totals_out_invoice",
    )
