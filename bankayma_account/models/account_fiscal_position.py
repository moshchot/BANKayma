# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    vendor_doc_mandatory = fields.Boolean(
        "Mandatory document upload",
        help="Check this field to have vendors with this fiscal position "
        "upload a document for every invoice",
    )
    vendor_doc_description = fields.Html()
    bankayma_tax_id = fields.Many2one(
        "account.tax",
        string="Impose tax",
        domain=[("type_tax_use", "=", "purchase")],
        check_company=True,
    )
    bankayma_tax_id_optional = fields.Boolean("Imposed tax optional")
    bankayma_tax_id_label = fields.Char(
        "Imposed tax label",
        translate=True,
        help="This is the label users will see in the portal and invoice forms",
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
