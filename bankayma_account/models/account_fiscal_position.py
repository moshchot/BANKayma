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
