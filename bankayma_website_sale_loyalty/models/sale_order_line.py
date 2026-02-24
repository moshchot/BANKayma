from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends()
    def _compute_name_short(self):
        result = super()._compute_name_short()
        for this in self:
            if this.reward_id.description:
                this.name_short = this.reward_id.description
        return result
