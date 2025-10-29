from odoo import fields, models


class BlogPost(models.Model):
    _inherit = "blog.post"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
