from odoo import fields, models


class WebsitePage(models.Model):
    _inherit = "website.page"

    name = fields.Char(translate=True)
