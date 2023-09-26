# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import http


class SumitController(http.Controller):
    _return_url = "/payment/sumit/return"

    @http.route(
        _return_url,
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        save_session=False,
    )
    def return_hook(self, **data):
        http.request.env["payment.transaction"].sudo()._handle_notification_data(
            "sumit", data
        )
        return http.request.redirect("/payment/status")
