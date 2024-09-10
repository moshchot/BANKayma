# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http


class CompaniesController(http.Controller):
    @http.route("/projects/<model(res.company):company>", website=True, auth="public")
    def render_company_page(self, company):
        return http.Response(
            template="bankayma_website.company_page",
            qcontext={"object": company.sudo()},
        )
