# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
import itertools
import random

from lxml import html
from markupsafe import Markup

from odoo import http


class ProjectsController(http.Controller):
    @http.route("/projects/<operating_unit>", website=True, auth="public")
    def render_project_page(self, operating_unit):
        routing_map = http.request.env["ir.http"].routing_map()
        operating_unit = (
            routing_map.converters["model"](routing_map, "operating.unit")
            .to_python(operating_unit)
            .with_env(http.request.env)
            .sudo()
        )
        Event = operating_unit.env["event.event"]
        EVENT_LIMIT = 4
        now = datetime.datetime.utcnow()
        event_domain = [
            ("is_published", "=", True),
            ("operating_unit_id", "=", operating_unit.id),
        ]
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
        next_object = operating_unit
        prev_object = operating_unit
        if operating_unit.category_id:
            operating_units = (
                operating_unit.category_id.operating_unit_ids - operating_unit
            )
            operating_units = operating_units.browse(
                random.sample(operating_units.ids, len(operating_units))
            )
            next_object = operating_units[:1] or operating_unit
            prev_object = operating_units[1:2] or operating_unit
        return http.Response(
            template="bankayma_website.project_page",
            qcontext={
                "object": operating_unit,
                "next_object": next_object,
                "prev_object": prev_object,
                "events": events[:EVENT_LIMIT],
                "render_dynamic_snippet": self._render_dynamic_snippet,
            },
        )

    @http.route("/projects/<operating_unit>/embed", website=True, auth="public")
    def render_project_page_embedded(self, operating_unit, **kwargs):
        result = self.render_project_page(operating_unit)
        result.template = "bankayma_website.project_page_embed"
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
                        {"name", "image_512"} & set(records._fields)
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
                b'<div class="d-flex flex-grow-0 flex-shrink-0 col-12 col-md-%s">'
                b"%s</div>"
                % (
                    str(col).encode("utf8"),
                    html.tostring(node),
                )
            )
        output += b"</div>"
        return Markup(output.decode("utf8"))

    def _search_combined(self, search=None, tags=None, limit=None, **kwargs):
        OperatingUnitTag = http.request.env["operating.unit.tag"].sudo()
        OperatingUnit = http.request.env["operating.unit"].sudo()

        other_languages = (
            http.request.env["res.lang"]
            .sudo()
            .search([("code", "!=", http.request.env.lang)])
            .mapped("code")
        )
        tag_ids = list(map(int, filter(None, (tags or "").split(","))))

        found_tags = OperatingUnitTag.search(
            [("display_name", "ilike", search), ("id", "not in", tag_ids)], limit=limit
        )
        for lang in other_languages:
            found_tags |= OperatingUnitTag.with_context(lang=lang).search(
                [
                    ("display_name", "ilike", search),
                    ("id", "not in", tag_ids + found_tags.ids),
                ],
                limit=limit,
            )

        domain = [
            ("parent_id", "!=", False),
            "|",
            ("category_id", "=", False),
            "&",
            ("category_id.company_hide_without_category", "=", False),
            ("category_id.category_show_on_website", "=", True),
        ]

        if tag_ids:
            domain.append(("tag_ids", "in", tag_ids))

        found = OperatingUnit.search(
            [("display_name", "ilike", search)] + domain, limit=limit
        )

        for lang in other_languages:
            found |= OperatingUnit.with_context(lang=lang).search(
                [("display_name", "ilike", search)] + domain, limit=limit
            )

        return found_tags, found

    @http.route("/projects/search", type="json", website=True, auth="public")
    def search_projects(self, search=None, tags=None, limit=5, **kwargs):
        tags, projects = self._search_combined(
            search=search, tags=tags, limit=limit, **kwargs
        )
        return [
            (
                dict(field="tags", name=record.display_name, value=record.id)
                if record._name == "operating.unit.tag"
                else dict(
                    url=record.website_link,
                    name=record.display_name,
                )
            )
            for record in list(itertools.chain(tags, projects))[:limit]
        ]

    @http.route("/projects", website=True, auth="public")
    def render_project_list(self, search=None, tags=None):
        _dummy, projects = self._search_combined(search=search, tags=tags)
        return http.Response(
            template="bankayma_website.project_list",
            qcontext={
                "objects": projects.browse(random.sample(projects.ids, len(projects))),
                "search": search,
                "tags": tags,
                "post_data": {
                    "tags": tags,
                },
            },
        )
