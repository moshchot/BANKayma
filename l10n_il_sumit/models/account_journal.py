# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models

from .sumit_account import SUMIT_DOCUMENT_TYPE_SELECTION


class AccountJournal(models.Model):
    _inherit = "account.journal"

    use_sumit = fields.Boolean("Push paid invoices to sumit")
    sumit_type = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        help="Invoices in this journal will create a document of the selected type in sumit",
        default="1",
    )
