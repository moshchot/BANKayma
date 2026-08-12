from odoo import http

from odoo.addons.website_event_sale.controllers import main as website_event_sale_main

from .website_sale import WebsiteSale


class WebsiteEventSaleController(website_event_sale_main.WebsiteEventSaleController):
    @http.route()
    def registration_confirm(self, event, **post):
        result = super().registration_confirm(event, **post)
        order = http.request.website.sale_get_order()
        if (
            result.status_code == 303
            and result.location == "/shop/checkout"
            and order.partner_id.id == http.request.website.user_id.sudo().partner_id.id
            and all(line.event_registration_ids for line in order.order_line)
        ):
            partner_vals = {
                "company_name": False,
                "team_id": http.request.website.salesteam_id.id,
            }
            for field_name in ("name", "email", "phone"):
                for registration in order.order_line.event_registration_ids:
                    if not registration[field_name]:
                        continue
                    partner_vals[field_name] = registration[field_name]
                    break
            partner_id = WebsiteSale()._create_or_edit_partner(
                partner_vals, type="invoice"
            )
            order.partner_id = http.request.env["res.partner"].sudo().browse(partner_id)
            result.location = "/shop/checkout?express=1"
        return result
