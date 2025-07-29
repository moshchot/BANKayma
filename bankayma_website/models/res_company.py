# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse, urlunparse

from odoo import api, fields, models

from odoo.addons.http_routing.models.ir_http import slugify


class ResCompany(models.Model):
    _inherit = "res.company"

    website_description = fields.Html(translate=True)
    seo_name = fields.Char("Website slug")
    website_link = fields.Char(compute="_compute_website_link")
    bankayma_website_subtitle = fields.Char("Subtitle", translate=True)
    bankayma_website_opening_hours = fields.Html("Opening hours", translate=True)
    bankayma_website_geolink = fields.Char("Geolink")
    bankayma_website_videolink = fields.Char("Video link")
    bankayma_website_image_ids = fields.Many2many(
        "ir.attachment", "res_company_bankayma_website_image_rel", string="Image slider"
    )
    bankayma_website_crew_partner_ids = fields.Many2many(
        "res.partner",
        "res_company_crew_res_partner_rel",
        string="Crew",
    )

    @api.depends("name", "seo_name")
    def _compute_website_link(self):
        for this in self:
            _id = getattr(this.id, "origin", this.id)
            if not _id:
                this.website_link = False
                continue
            base_url = urlparse(self.get_base_url())
            this.website_link = urlunparse(
                (
                    base_url.scheme,
                    base_url.netloc,
                    f"projects/{slugify(this.seo_name or this.name)}-{_id}",
                    None,
                    None,
                    None,
                )
            )
