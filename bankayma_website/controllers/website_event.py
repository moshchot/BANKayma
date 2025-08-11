# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http, tools

from odoo.addons.website_event.controllers import main

from .main import ProjectsController


class WebsiteEventController(main.WebsiteEventController):
    @http.route()
    def events(self, page=1, projects=None, **searches):
        http.request.website = http.request.website.with_context(
            bankayma_event_projects=projects
        )
        result = super().events(page=page, **dict(projects=projects, **searches))
        (
            ou_tags_available,
            ous_available,
        ) = ProjectsController._search_combined(self)
        result.qcontext["ous_available"] = ous_available
        result.qcontext["ous_selected"] = ous_available.browse(
            projects and tools.safe_eval.const_eval(projects) or []
        )
        result.qcontext["ous_tags_available"] = ou_tags_available
        return result
