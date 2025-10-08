from ast import literal_eval

from odoo import api, models


class Event(models.Model):
    _inherit = "event.event"

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        companies = website.env.context.get("bankayma_event_projects")
        search_companies = self.env["res.company"].sudo()
        if companies:
            company_ids = literal_eval(companies)
            if company_ids:
                result["base_domain"].append([("company_id", "in", company_ids)])
                search_companies = self.env["res.company"].sudo().browse(company_ids)
        return dict(result, search_companies=search_companies)
