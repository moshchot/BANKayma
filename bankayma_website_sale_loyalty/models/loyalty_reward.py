from odoo import _, api, exceptions, fields, models


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    bankayma_website_sale_company_id = fields.Many2one(
        "res.company", compute="_compute_bankayma_website_sale_company_id"
    )

    @api.depends("discount_product_ids", "discount_line_product_id")
    def _compute_bankayma_website_sale_company_id(self):
        for this in self:
            this.bankayma_website_sale_company_id = (
                this.discount_product_ids.bankayma_website_sale_company_id
                or this.discount_line_product_id.bankayma_website_sale_company_id
                or this.bankayma_website_sale_company_id
                or this.program_id.bankayma_website_sale_company_id
            )

    @api.constrains("discount_line_product_id", "discount_product_ids")
    def _check_products(self):
        for this in self:
            if not this.discount_product_ids or not this.discount_line_product_id:
                continue
            if (
                this.discount_line_product_id.bankayma_website_sale_company_id
                != this.discount_product_ids.bankayma_website_sale_company_id
            ):
                raise exceptions.ValidationError(
                    _(
                        "Discount product and discounted products must have the "
                        "same webshop company"
                    )
                )

    def _get_discount_product_values(self):
        return [
            dict(
                vals,
                bankayma_website_sale_company_id=(
                    this.program_id.bankayma_website_sale_company_id.id
                ),
            )
            for vals, this in zip(super()._get_discount_product_values(), self)
        ]
