# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bankayma_website_sale_company_id = fields.Many2one(
        "res.company", compute="_compute_bankayma_website_sale_company_id"
    )

    @api.depends(
        "product_id.bankayma_website_sale_company_id",
        "sale_line_ids.event_id.company_id",
    )
    def _compute_bankayma_website_sale_company_id(self):
        for this in self:
            this.bankayma_website_sale_company_id = (
                this.product_id.bankayma_website_sale_company_id
                or this.sale_line_ids.event_id.company_id
            )
