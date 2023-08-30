# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.l10n_il_sumit.models.sumit_account import SUMIT_DOCUMENT_TYPE_SELECTION


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sumit_type = fields.Selection(
        SUMIT_DOCUMENT_TYPE_SELECTION,
        string="Override sumit type",
        help="If you set a value here, it will override the journal's sumit type for "
        "invoices with this product",
    )
