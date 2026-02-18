from odoo import fields, models


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    discount_line_product_id = fields.Many2one(required=True)
