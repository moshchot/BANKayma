# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    name = fields.Char(translate=True)

    def _search_get_details(self, search_type, order, options):
        if search_type == "res.company.tag":
            return [
                {
                    "model": "res.company.tag",
                    "fetch_fields": ["name"],
                    "mapping": {
                        "name": {"name": "name", "type": "text", "match": True},
                        "website_url": {"name": "website_url"},
                    },
                    "icon": "fa-tag",
                }
            ]
        return super()._search_get_details(search_type, order, options)
