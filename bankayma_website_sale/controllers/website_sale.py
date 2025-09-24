# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _shop_get_query_url_kwargs(self, *args, **kwargs):
        result = super()._shop_get_query_url_kwargs(*args, **kwargs)
        if "project" in kwargs:
            result["project"] = kwargs["project"]
        return result

    def _get_search_options(self, *args, **kwargs):
        result = super()._get_search_options(*args, **kwargs)
        if "project" in kwargs:
            result["project"] = kwargs["project"]
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
