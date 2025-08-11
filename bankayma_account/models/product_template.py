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
    sumit_recurrence = fields.Selection(
        [("daily", "Daily"), ("monthly", "Monthly")],
        string="Recurrence",
    )
    sumit_recurrence_interval = fields.Integer(string="Interval")

    def _get_product_accounts(self):
        """
        Implement BK's OU specific accounts
        """
        result = super()._get_product_accounts()
        ou = (
            self.env["operating.unit"].browse(
                self.env.context.get("default_operating_unit_id")
                or self.env.context.get("operating_unit_id")
                or []
            )
            or self.env.user._get_default_operating_unit()
        )
        if ou and self.default_code:
            ou_account = self.env["account.account"].search(
                [
                    ("is_ou_specific", "=", True),
                    ("code", "=", ou.code + self.default_code),
                ]
            )
            for key in ("income", "expense"):
                result[key] = ou_account or result[key]
        return result
