# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from operator import itemgetter

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
                    "field_names": ",".join(
                        {"display_name", "image_512"} & set(records._fields)
                    ),
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
    def render_company_list(self, search=None, category=None, tags=None):
        ResCompany = http.request.env["res.company"].sudo()
        ResCompanyCategory = http.request.env["res.company.category"].sudo()
        ResCompanyTag = http.request.env["res.company.tag"].sudo()

        domain = [("parent_id", "!=", False)]
        if category:
            if category.isdigit() and ResCompanyCategory.browse(int(category)).exists():
                domain.append(("category_id", "=", int(category)))
            else:
                domain.append(("category_id", "ilike", category))
        else:
            domain += [
                "|",
                ("category_id", "=", False),
                ("category_id.company_hide_without_category", "=", False),
            ]

        if tags:
            tags_found = ResCompanyTag.browse(
                map(
                    itemgetter(0),
                    (
                        name_get
                        for tag in tags.split()
                        for name_get in ResCompanyTag.name_search(tag)
                    ),
                )
            )

            domain += [("tag_ids", "child_of", tags_found.ids)]

        domain += [
            "|",
            ("category_id", "=", False),
            ("category_id.category_show_on_website", "=", True),
        ]

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
                "tags": tags,
            },
        )
