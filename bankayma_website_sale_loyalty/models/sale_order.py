from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _discountable_order(self, reward):
        lines = self.order_line
        self._cache["order_line"] = tuple(
            lines.filtered(
                lambda x: not x.product_id
                or x.product_id.bankayma_website_sale_company_id
                == reward.bankayma_website_sale_company_id
            ).ids
        )
        result = super()._discountable_order(reward)
        self.invalidate_recordset(["order_line"])
        return result
