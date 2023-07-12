# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    name = fields.Char(translate=True)
    invoice_auto_validation = fields.Boolean(default=False)
    intercompany_sale_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany sale journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "sale")],
    )
    intercompany_purchase_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany purchase journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "purchase")],
    )
    overhead_journal_id = fields.Many2one(
        "account.journal",
        "Overhead journal",
        help="Overhead invoices will be created in this journal",
        domain=[("type", "=", "sale")],
    )
    overhead_account_id = fields.Many2one(
        "account.account",
        "Overhead account",
        help="Overhead invoice lines will have this account",
    )
    overhead_payment_journal_id = fields.Many2one(
        "account.journal",
        "Overhead payment journal",
        help="Overhead invoices will be paid in this journal",
        domain=[("type", "=", "bank")],
    )
