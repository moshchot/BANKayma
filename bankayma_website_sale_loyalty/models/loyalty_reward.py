from odoo import fields, models


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        related="program_id.operating_unit_id",
    )

    def _get_discount_product_values(self):
        return [
            dict(
                vals,
                operating_unit_id=(this.program_id.operating_unit_id.id),
            )
            for vals, this in zip(
                super()._get_discount_product_values(), self, strict=False
            )
        ]
