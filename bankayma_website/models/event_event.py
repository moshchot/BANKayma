from odoo import api, models, tools


class Event(models.Model):
    _inherit = ["event.event", "bankayma.search.drop.company.mixin"]
    _name = "event.event"

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        ou_ids_context = website.env.context.get("bankayma_event_projects")
        if ou_ids_context:
            ou_ids = tools.safe_eval.const_eval(ou_ids_context)
            if ou_ids:
                result["base_domain"].append([("operating_unit_id", "in", ou_ids)])
        return result
