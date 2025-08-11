# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import quote_plus

from odoo import api, fields, models

from odoo.addons.web_editor.tools import get_video_url_data


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

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
        "ir.attachment",
        "operating_unit_bankayma_website_image_rel",
        string="Image slider",
    )
    bankayma_website_crew_partner_ids = fields.Many2many(
        "res.partner",
        "operating_unit_crew_res_partner_rel",
        string="Crew",
    )
    bankayma_website_backer_partner_ids = fields.Many2many(
        "res.partner",
        compute="_compute_bankayma_website_backer_partner_ids",
        inverse="_inverse_bankayma_website_backer_partner_ids",
        string="Backers",
    )
    logo = fields.Image(related="partner_id.avatar_128")
    street = fields.Char(related="partner_id.street")
    city = fields.Char(related="partner_id.city")
    country_id = fields.Many2one(related="partner_id.country_id")
    email = fields.Char(related="partner_id.email")
    phone = fields.Char(related="partner_id.phone")
    website = fields.Char(related="partner_id.website")
    social_twitter = fields.Char()
    social_facebook = fields.Char()
    social_instagram = fields.Char()
    social_youtube = fields.Char()

    @api.depends("name", "seo_name")
    def _compute_website_link(self):
        for this in self:
            _id = getattr(this.id, "origin", this.id)
            if not _id:
                this.website_link = False
                continue
            this.website_link = "/projects/{}-{}".format(
                self.env["ir.http"]._slugify(this.seo_name or this.name), _id
            )

    @api.depends("partner_id.street", "partner_id.city", "partner_id.country_id")
    def _compute_bankayma_website_geolink(self):
        for this in self:
            if (
                not this.partner_id.country_id
                or not this.partner_id.city
                or not this.partner_id.street
            ):
                this.bankayma_website_geolink = False
            else:
                url_template = (
                    "//maps.google.com/maps?q={}&t=m&z=12&ie=UTF8&iwloc=&output=embed"
                )
                this.bankayma_website_geolink = url_template.format(
                    quote_plus(
                        f"{this.partner_id.street} "
                        f"{this.partner_id.city} "
                        f"{this.partner_id.country_id.name}"
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
                lambda x, this=this: (
                    x.type_id == rel_type
                    and x.other_partner_id
                    not in this.bankayma_website_backer_partner_ids
                )
            ).unlink()
            for partner in this.bankayma_website_backer_partner_ids:
                if not this.partner_id.relation_all_ids.filtered(
                    lambda x, partner=partner: (
                        x.type_id == rel_type and x.other_partner_id == partner
                    )
                ):
                    self.env["res.partner.relation.all"].create(
                        {
                            "type_id": rel_type.id,
                            "other_partner_id": partner.id,
                            "this_partner_id": this.partner_id.id,
                            "is_inverse": True,
                        }
                    )
