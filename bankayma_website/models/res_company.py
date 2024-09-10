# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse, urlunparse

from odoo import api, fields, models

from odoo.addons.http_routing.models.ir_http import slug


class ResCompany(models.Model):
    _inherit = "res.company"

    website_description = fields.Html()
    website_link = fields.Char(compute="_compute_website_link")

    @api.depends("name")
    def _compute_website_link(self):
        for this in self:
            base_url = urlparse(self.get_base_url())
            this.website_link = urlunparse(
                (
                    base_url.scheme,
                    base_url.netloc,
                    "projects/" + slug(this),
                    None,
                    None,
                    None,
                )
            )
