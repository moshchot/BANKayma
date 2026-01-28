from odoo import models


class BlogBlog(models.Model):
    _inherit = "blog.blog"
    _mail_post_access = "read"
