# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bankayma_website_sale_company_id = fields.Many2one(
        "res.company", string="Company (webshop)"
    )

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        if "project" in options:
            result["base_domain"].append(
                [("bankayma_website_sale_company_id", "=", int(options["project"]))]
            )
        else:
            result["base_domain"].append(
                [("bankayma_website_sale_company_id", "=", False)]
            )
        return result
