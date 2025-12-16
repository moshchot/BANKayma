from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _prepare_values(self, limit=None, search_domain=None):
        self = self.with_context(bankayma_search_drop_company=True)
        return super()._prepare_values(limit=limit, search_domain=search_domain)
