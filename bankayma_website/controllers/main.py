# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import itertools

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

    def _search_combined(self, search=None, tags=None, limit=None, **kwargs):
        ResCompanyTag = http.request.env["res.company.tag"].sudo()
        ResCompany = http.request.env["res.company"].sudo()

        other_languages = (
            http.request.env["res.lang"]
            .sudo()
            .search([("code", "!=", http.request.env.lang)])
            .mapped("code")
        )
        tag_ids = list(map(int, filter(None, (tags or "").split(","))))

        found_tags = ResCompanyTag.browse(
            ResCompanyTag._name_search(
                search, args=[("id", "not in", tag_ids)], limit=limit
            )
        )
        for lang in other_languages:
            found_tags |= ResCompanyTag.browse(
                ResCompanyTag.with_context(lang=lang)._name_search(
                    search, args=[("id", "not in", tag_ids)], limit=limit
                )
            )

        companies_domain = [
            ("parent_id", "!=", False),
            "|",
            ("category_id", "=", False),
            ("category_id.company_hide_without_category", "=", False),
        ]

        if tag_ids:
            companies_domain.append(("tag_ids", "in", tag_ids))

        found_companies = ResCompany.browse(
            ResCompany._name_search(search, args=companies_domain, limit=limit)
        )
        for lang in other_languages:
            found_companies |= ResCompany.browse(
                ResCompany.with_context(lang=lang)._name_search(
                    search, args=companies_domain, limit=limit
                )
            )

        return found_tags, found_companies

    @http.route("/projects/search", type="json", website=True, auth="public")
    def search_company(self, search=None, tags=None, limit=5, **kwargs):
        tags, companies = self._search_combined(
            search=search, tags=tags, limit=limit, **kwargs
        )
        return [
            (
                dict(field="tags", name=record.display_name, value=record.id)
                if record._name == "res.company.tag"
                else dict(
                    url=record.website_link,
                    name=record.display_name,
                )
            )
            for record in list(itertools.chain(tags, companies))[:limit]
        ]

    @http.route("/projects", website=True, auth="public")
    def render_company_list(self, search=None, tags=None):
        _dummy, companies = self._search_combined(search=search, tags=tags)
        return http.Response(
            template="bankayma_website.company_list",
            qcontext={
                "objects": companies,
                "search": search,
                "tags": tags,
                "post_data": {
                    "tags": tags,
                },
            },
        )
