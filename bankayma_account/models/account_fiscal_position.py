# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    code = fields.Char()
    vendor_doc_mandatory = fields.Boolean(
        "Mandatory document upload",
        help="Check this field to have vendors with this fiscal position "
        "upload a document for every invoice",
    )
    vendor_doc_description = fields.Html()
    bankayma_tax_ids = fields.Many2many(
        "account.tax",
        "account_fiscal_position_bankayma_tax",
        "fiscal_position_id",
        "tax_id",
        string="Impose tax",
        domain=[("type_tax_use", "=", "purchase")],
        check_company=True,
    )
    optional_tax_group_ids = fields.Many2many(
        "account.tax.group",
        "account_fiscal_position_optional_tax_group",
        "fiscal_position_id",
        "tax_group_id",
        string="Optional tax groups",
    )
    bankayma_deduct_tax = fields.Boolean("Tax deduction")
    bankayma_deduct_tax_use_max_amount = fields.Boolean("Use max amount")
    bankayma_deduct_tax_account_id = fields.Many2one(
        "account.account",
        string="Tax account",
        check_company=True,
    )
    bankayma_deduct_tax_group_id = fields.Many2one(
        "account.tax.group", string="Tax group"
    )
