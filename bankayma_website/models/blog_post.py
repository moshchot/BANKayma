from odoo import fields, models


class BlogPost(models.Model):
    _inherit = ["blog.post", "bankayma.search.drop.company.mixin"]
    _name = "blog.post"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
