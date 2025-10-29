# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import quote_plus

from odoo import api, fields, models

from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.web_editor.tools import get_video_url_data


class ResCompany(models.Model):
    _inherit = "res.company"

    website_description = fields.Html(translate=True)
    seo_name = fields.Char("Website slug")
    website_link = fields.Char(compute="_compute_website_link")
    bankayma_website_subtitle = fields.Char("Subtitle", translate=True)
    bankayma_inception_year = fields.Integer("Inception year")
    bankayma_website_cover = fields.Image("Cover image")
    bankayma_website_opening_hours = fields.Html("Opening hours", translate=True)
    bankayma_website_geolink = fields.Char(
        "Geolink", compute="_compute_bankayma_website_geolink"
    )
    bankayma_website_videolink = fields.Char("Video link")
    bankayma_website_videolink_embed = fields.Char(
        compute="_compute_bankayma_website_videolink_embed"
    )
    bankayma_website_image_ids = fields.Many2many(
        "ir.attachment", "res_company_bankayma_website_image_rel", string="Image slider"
    )
    bankayma_website_crew_partner_ids = fields.Many2many(
        "res.partner",
        "res_company_crew_res_partner_rel",
        string="Crew",
    )
    bankayma_website_backer_partner_ids = fields.Many2many(
        "res.partner",
        compute="_compute_bankayma_website_backer_partner_ids",
        inverse="_inverse_bankayma_website_backer_partner_ids",
        string="Backers",
    )

    @api.depends("name", "seo_name")
    def _compute_website_link(self):
        for this in self:
            _id = getattr(this.id, "origin", this.id)
            if not _id:
                this.website_link = False
                continue
            this.website_link = f"/projects/{slugify(this.seo_name or this.name)}-{_id}"

    @api.depends("street", "city", "country_id")
    def _compute_bankayma_website_geolink(self):
        for this in self:
            if not this.country_id or not this.city or not this.street:
                this.bankayma_website_geolink = False
            else:
                this.bankayma_website_geolink = (
                    "//maps.google.com/maps?q=%s&t=m&z=12&ie=UTF8&iwloc=&output=embed"
                    % quote_plus(
                        "%s %s %s" % (this.street, this.city, this.country_id.name),
                    )
                )

    @api.depends("bankayma_website_videolink")
    def _compute_bankayma_website_videolink_embed(self):
        for this in self:
            video_data = get_video_url_data(this.bankayma_website_videolink)
            this.bankayma_website_videolink_embed = (
                video_data.get("embed_url") or this.bankayma_website_videolink
            )

    def _compute_bankayma_website_backer_partner_ids(self):
        rel_type = self.env.ref("bankayma_website.rel_type_backer")
        for this in self:
            this.bankayma_website_backer_partner_ids = (
                this.partner_id.relation_all_ids.filtered(
                    lambda x: x.type_id == rel_type and x.is_inverse
                ).other_partner_id
            )

    def _inverse_bankayma_website_backer_partner_ids(self):
        rel_type = self.env.ref("bankayma_website.rel_type_backer")
        for this in self:
            this.partner_id.relation_all_ids.filtered(
                lambda x: x.type_id == rel_type
                and x.other_partner_id not in this.bankayma_website_backer_partner_ids
            ).unlink()
            for partner in this.bankayma_website_backer_partner_ids:
                if not this.partner_id.relation_all_ids.filtered(
                    lambda x: x.type_id == rel_type and x.other_partner_id == partner
                ):
                    self.env["res.partner.relation.all"].create(
                        {
                            "type_id": rel_type.id,
                            "other_partner_id": partner.id,
                            "this_partner_id": this.partner_id.id,
                            "is_inverse": True,
                        }
                    )
