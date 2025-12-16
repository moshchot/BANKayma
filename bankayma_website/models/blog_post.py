from odoo import fields, models

from odoo.addons.http_routing.models.ir_http import slug


class BlogPost(models.Model):
    _inherit = ["blog.post", "bankayma.search.drop.company.mixin"]
    _name = "blog.post"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    def _compute_website_url(self):
        for this in self:
            this.website_url = "/news/%s" % slug(this)
