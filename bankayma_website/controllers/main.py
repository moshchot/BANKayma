# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
import itertools
import random

from lxml import html
from markupsafe import Markup

from odoo import http


class CompaniesController(http.Controller):
    @http.route("/projects/<model(res.company):company>", website=True, auth="public")
    def render_company_page(self, company):
        company = company.sudo()
        Event = company.env["event.event"]
        EVENT_LIMIT = 4
        now = datetime.datetime.utcnow()
        event_domain = [("is_published", "=", True), ("company_id", "=", company.id)]
        events = Event.search(
            event_domain + [("date_end", ">=", now)], limit=EVENT_LIMIT
        )
        if len(events) < EVENT_LIMIT:
            events = (
                Event.search(
                    event_domain + [("date_end", "<", now)],
                    order=None if events else "date_begin desc",
                    limit=EVENT_LIMIT - len(events),
                )
                + events
            )
        next_object = company
        prev_object = company
        if company.category_id:
            companies = company.category_id.company_ids - company
            companies = companies.browse(random.sample(companies.ids, len(companies)))
            next_object = companies[:1] or company
            prev_object = companies[1:2] or company
        return http.Response(
            template="bankayma_website.company_page",
            qcontext={
                "object": company,
                "next_object": next_object,
                "prev_object": prev_object,
                "events": events[:EVENT_LIMIT],
                "render_dynamic_snippet": self._render_dynamic_snippet,
            },
        )

    @http.route(
        "/projects/<model(res.company):company>/embed", website=True, auth="public"
    )
    def render_company_page_embedded(self, company, **kwargs):
        result = self.render_company_page(company)
        result.template = "bankayma_website.company_page_embed"
        result.qcontext["no_header"] = True
        result.qcontext["no_footer"] = True
        for _dummy, arg in http.request.env[
            "bankayma.project.page.embed.code.option"
        ]._get_options():
            result.qcontext[f"show_{arg}"] = kwargs.get(arg)
        return result

    def _render_dynamic_snippet(self, xmlid, records, col=3):
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
        for node in html.fromstring(f"<root>{xml}</root>").getchildren():
            output += (
                b'<div class="d-flex flex-grow-0 flex-shrink-0 col-12 col-md-%s">%s</div>'
                % (
                    str(col).encode("utf8"),
                    html.tostring(node),
                )
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
                "objects": companies.browse(
                    random.sample(companies.ids, len(companies))
                ),
                "search": search,
                "tags": tags,
                "post_data": {
                    "tags": tags,
                },
            },
        )
