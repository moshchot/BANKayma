# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from operator import itemgetter

from odoo import models


class ResCompanyTag(models.Model):
    _inherit = ["res.company.tag", "website.searchable.mixin"]
    _name = "res.company.tag"

    def _search_fetch(self, search_detail, search, limit, order):
        ids = list(map(itemgetter(0), self.name_search(search, limit=limit)))
        result = self.search([("id", "in", ids)])
        return result, len(result)

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        return [
            {
                "_fa": "fa-tag",
                "_mapping": mapping,
                "name": this.display_name,
                "website_url": "/projects?tags=" + this.name,
            }
            for this in self
        ]
