import random

from odoo import models

from odoo.addons.website.models import ir_http


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _filter_records_to_values(self, records, is_sample=False):
        website = ir_http.get_request_website()
        if (
            isinstance(records, models.Model)
            and records._name in ("product.product", "product.template")
            and website
        ):
            records = records.filtered_domain(website.sale_product_domain())
        return super()._filter_records_to_values(records, is_sample=is_sample)

    def _get_products_random(self, website, limit, domain, context):
        products = (
            self.env["product.product"]
            .with_context(display_default_code=False, add2cart_rerender=False)
            .search(domain)
        )
        return products.browse(random.sample(products.ids, len(products)))[:limit]
