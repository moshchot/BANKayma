from odoo import models


class Website(models.Model):
    _inherit = "website"

    def sale_product_domain(self):
        result = super().sale_product_domain()
        result += [("bankayma_website_sale_hide", "=", False)]
        return result
