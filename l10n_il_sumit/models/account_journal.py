# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models

from .sumit_account import SUMIT_DOCUMENT_TYPE_SELECTION


class AccountJournal(models.Model):
    _inherit = "account.journal"

    use_sumit = fields.Boolean("Push paid invoices to sumit")
    sumit_type = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (default)",
        help="Invoices in this journal will create a document of the selected type in "
        "sumit",
        default="1",
    )
    sumit_type_entry = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (entry)",
        help="Moves of type entry in this journal will create a document of the "
        "selected type in sumit",
    )
    sumit_type_out_invoice = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (customer invoice)",
        help="Customer invoices in this journal will create a document of the selected "
        "type in sumit",
    )
    sumit_type_out_refund = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (customer credit note)",
        help="Customer credit notes in this journal will create a document of the "
        "selected type in sumit",
    )
    sumit_type_in_invoice = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (vendor bill)",
        help="Vendor bills in this journal will create a document of the selected type "
        "in sumit",
    )
    sumit_type_in_refund = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (vendor credit note)",
        help="Vendor credit notes in this journal will create a document of the "
        "selected type in sumit",
    )
    sumit_type_out_receipt = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (sales receipt)",
        help="Sales receipts in this journal will create a document of the selected "
        "type in sumit",
    )
    sumit_type_in_receipt = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Sumit type (purchase receipt)",
        help="Purchase receipts in this journal will create a document of the selected "
        "type in sumit",
    )
