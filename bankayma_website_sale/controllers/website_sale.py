# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.bankayma_website.controllers.main import CompaniesController
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _shop_get_query_url_kwargs(self, *args, **kwargs):
        result = super()._shop_get_query_url_kwargs(*args, **kwargs)
        if "project" in kwargs:
            result["project"] = kwargs["project"]
        if "product_tag" in kwargs:
            result["product_tag"] = kwargs["product_tag"]
        return result

    def _get_search_options(self, *args, **kwargs):
        result = super()._get_search_options(*args, **kwargs)
        if "project" in kwargs:
            result["project"] = kwargs["project"]
        if "product_tag" in kwargs:
            result["product_tag"] = kwargs["product_tag"]
        return result

    def _get_additional_shop_values(self, values):
        result = super()._get_additional_shop_values(values)
        (
            company_tags_available,
            companies_available,
        ) = CompaniesController._search_combined(self)
        result.update(
            company_tags_available=company_tags_available,
            companies_available=companies_available,
            product_tags_available=request.env["product.tag"].search(
                [
                    (
                        "product_template_ids.bankayma_website_sale_company_id",
                        "in",
                        companies_available.ids,
                    )
                ]
            ),
        )
        return result

    def _get_additional_extra_shop_values(self, values, **post):
        result = super()._get_additional_extra_shop_values(values, **post)
        result.update(
            project=request.env["res.company"]
            .sudo()
            .browse(int(post.get("project", 0)) or [])
        )
        result.update(
            product_tag=request.env["product.tag"]
            .sudo()
            .browse(int(post.get("product_tag", 0)) or [])
        )
        return result

    def _create_or_edit_partner(self, *args, **kwargs):
        partner_id = super()._create_or_edit_partner(*args, **kwargs)
        request.env["res.partner"].browse(partner_id).sudo().company_id = False
        return partner_id

    def _checkout_form_save(self, mode, *args, **kwargs):
        partner_id = super()._checkout_form_save(mode, *args, **kwargs)
        partner = request.env["res.partner"].browse(partner_id).sudo()
        if partner.company_id:
            partner.company_id = False
        return partner_id

    def _get_mandatory_fields_billing(self, country_id=False):
        return self._bankayma_skip_checkout_address_required_fields(
            super()._get_mandatory_fields_billing(country_id=country_id)
        )

    def _get_mandatory_fields_shipping(self, country_id=False):
        return self._bankayma_skip_checkout_address_required_fields(
            super()._get_mandatory_fields_shipping(country_id=country_id)
        )

    def _bankayma_skip_checkout_address_required_fields(self, required_fields):
        order = request.website.sale_get_order()
        if not order._bankayma_checkout_address_required():
            return [
                field_name
                for field_name in required_fields
                if field_name not in ("street", "city", "country_id", "zip")
            ]
        return required_fields
