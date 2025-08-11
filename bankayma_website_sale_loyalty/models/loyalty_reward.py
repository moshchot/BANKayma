from odoo import _, api, exceptions, fields, models


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    operating_unit_id = fields.Many2one(
        "operating.unit", compute="_compute_operating_unit_id"
    )

    @api.depends("discount_product_ids", "discount_line_product_id")
    def _compute_operating_unit_id(self):
        for this in self:
            this.operating_unit_id = (
                this.discount_product_ids.operating_unit_id
                or this.discount_line_product_id.operating_unit_id
                or this.operating_unit_id
                or this.program_id.operating_unit_id
            )

    @api.constrains("discount_line_product_id", "discount_product_ids")
    def _check_products(self):
        for this in self:
            if not this.discount_product_ids or not this.discount_line_product_id:
                continue
            if (
                this.discount_line_product_id.operating_unit_id
                != this.discount_product_ids.operating_unit_id
            ):
                raise exceptions.ValidationError(
                    _(
                        "Discount product and discounted products must have the "
                        "same operating unit"
                    )
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
