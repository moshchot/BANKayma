# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import html
from markupsafe import Markup

from odoo import http


class CompaniesController(http.Controller):
    @http.route("/projects/<model(res.company):company>", website=True, auth="public")
    def render_company_page(self, company):
        return http.Response(
            template="bankayma_website.company_page",
            qcontext={
                "object": company.sudo(),
                "render_dynamic_snippet": self._render_dynamic_snippet,
            },
        )

    def _render_dynamic_snippet(self, xmlid, records):
        data = (
            http.request.env["website.snippet.filter"]
            .new(
                {
                    "model_name": records._name,
                    "field_names": "display_name",
                }
            )
            ._filter_records_to_values(records)
        )
        xml = (
            http.request.env["ir.qweb"]
            .with_context(inherit_branding=False)
            ._render(xmlid, {"records": data})
        )
        output = b'<div class="row my-4">'
        for node in html.fromstring(xml).getchildren():
            output += (
                b'<div class="d-flex flex-grow-0 flex-shrink-0 col-3">%s</div>'
                % html.tostring(node)
            )
        output += b"</div>"
        return Markup(output.decode("utf8"))

    @http.route("/projects", website=True, auth="public")
    def render_company_list(self, search=None, category=None):
        ResCompany = http.request.env["res.company"].sudo()
        ResCompanyCategory = http.request.env["res.company.category"].sudo()

        domain = [("parent_id", "!=", False)]
        if category:
            if category.isdigit() and ResCompanyCategory.browse(int(category)).exists():
                domain.append(("category_id", "=", int(category)))
            else:
                domain.append(("category_id", "ilike", category))

        companies = ResCompany.browse(
            ResCompany._name_search(
                name=search or "",
                args=domain,
            )
        )
        return http.Response(
            template="bankayma_website.company_list",
            qcontext={
                "objects": companies,
                "search": search,
                "category": category,
            },
        )
