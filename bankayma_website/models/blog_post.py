import json

from odoo import api, fields, http, models


class BlogPost(models.Model):
    _inherit = ["blog.post", "bankayma.search.drop.company.mixin"]
    _name = "blog.post"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    def _compute_website_url(self):
        slug = self.env["ir.http"]._slug
        for this in self:
            this.website_url = f"/news/{slug(this)}"

    @api.model
    def _search_build_domain(self, domain_list, search, fields, extra=None):
        result = super()._search_build_domain(domain_list, search, fields, extra=extra)
        if http.request and http.request.params.get("projects"):
            result.append(
                ("company_id", "in", json.loads(http.request.params["projects"]))
            )
        return result
