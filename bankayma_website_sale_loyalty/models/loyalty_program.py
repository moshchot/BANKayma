from odoo import _, api, fields, models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    program_type = fields.Selection(default="promo_code")
    bankayma_program_type = fields.Selection(
        selection=[
            ("promo_code_product", "Discount code for product(s)"),
            ("promo_code_company", "Discount code for company"),
        ],
        string="Coupon Type",
        default="promo_code_product",
    )
    bankayma_promo_code = fields.Char("Promo Code")
    bankayma_discount_type = fields.Selection(
        selection=[("percentage", "Percentage"), ("amount", "Amount")],
        string="Discount Type",
        default="percentage",
    )
    bankayma_discount_value = fields.Float()
    bankayma_discount_name = fields.Char("Name on order", translate=True)
    bankayma_website_sale_company_id = fields.Many2one(
        "res.company",
        string="Webshop company",
    )
    bankayma_product_ids = fields.Many2many(
        "product.product",
        relation="bankayma_loyalty_program_product_product",
        string="Products",
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for this, vals in zip(result, vals_list):
            if any(key.startswith("bankayma_") for key in vals):
                this._bankayma_update_rules_rewards()
        return result

    def write(self, vals):
        result = super().write(vals)
        if any(key.startswith("bankayma_") for key in vals):
            for this in self:
                this._bankayma_update_rules_rewards()
        return result

    def copy_data(self, default):
        if self.bankayma_promo_code:
            new_code = _("%s (Copy)") % self.bankayma_promo_code
            default = dict(
                default or {},
                bankayma_promo_code=new_code,
                rule_ids=[
                    fields.Command.create(
                        self.rule_ids[:1].copy_data({"code": new_code})[0]
                    )
                ],
                reward_ids=[
                    fields.Command.create(
                        self.reward_ids[:1].copy_data(
                            {
                                "discount_line_product_id": self.reward_ids[:1]
                                .discount_line_product_id.copy()
                                .id
                            }
                        )[0]
                    )
                ],
            )
        return super().copy_data(default)

    def _bankayma_update_rules_rewards(self):
        self.ensure_one()
        rule_vals = {
            "code": self.bankayma_promo_code,
            "reward_point_mode": "unit",
        }
        reward_vals = {
            "reward_type": "discount",
            "discount": self.bankayma_discount_value,
            "discount_mode": "percent"
            if self.bankayma_discount_type == "percentage"
            else "per_order",
            "discount_applicability": "order"
            if self.bankayma_program_type == "promo_code_company"
            else "specific",
            "description": self.bankayma_discount_name,
            "discount_product_ids": [fields.Command.set(self.bankayma_product_ids.ids)],
        }
        self.write(
            {
                "rule_ids": [fields.Command.update(self.rule_ids.id, rule_vals)]
                if len(self.rule_ids) == 1
                else [fields.Command.clear(), fields.Command.create(rule_vals)],
                "reward_ids": [fields.Command.update(self.reward_ids.id, reward_vals)]
                if len(self.reward_ids) == 1
                else [fields.Command.clear(), fields.Command.create(reward_vals)],
            }
        )
        for lang in self.env["res.lang"].search([]):
            self_with_lang = self.with_context(lang=lang.code)
            if (
                self_with_lang.reward_ids.description
                != self_with_lang.bankayma_discount_name
            ):
                self_with_lang.reward_ids.description = (
                    self_with_lang.bankayma_discount_name
                )
