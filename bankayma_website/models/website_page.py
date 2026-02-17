from odoo import api, fields, models


class WebsitePage(models.Model):
    _inherit = "website.page"

    name = fields.Char(translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for this in result:
            if not this.name and this.view_id.name:
                this.name = this.view_id.name
        return result
