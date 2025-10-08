# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import http

from odoo.addons.website_event.controllers import main

from .main import CompaniesController


class WebsiteEventController(main.WebsiteEventController):
    @http.route()
    def events(self, page=1, projects=None, **searches):
        http.request.website = http.request.website.with_context(
            bankayma_event_projects=projects
        )
        result = super().events(page=page, **dict(projects=projects, **searches))
        (
            company_tags_available,
            companies_available,
        ) = CompaniesController._search_combined(self)
        result.qcontext["companies_available"] = companies_available
        result.qcontext["companies_selected"] = companies_available.browse(
            projects and literal_eval(projects) or []
        )
        result.qcontext["company_tags_available"] = company_tags_available
        return result
