from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestWebsiteSaleLoyalty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.program = cls.env["loyalty.program"].create(
            {
                "name": "Test program",
                "bankayma_discount_name": "Test program",
                "bankayma_promo_code": "TEST00042",
                "bankayma_discount_value": 20,
                "currency_id": cls.env.company.currency_id.id,
                "operating_unit_id": cls.env.ref(
                    "operating_unit.b2c_operating_unit"
                ).id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env["res.partner"].search([], limit=1).id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.env.ref(
                                "bankayma_website_sale.product_b2b"
                            ).id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.env.ref(
                                "bankayma_website_sale.product_b2c"
                            ).id,
                        }
                    ),
                ],
            }
        )
        cls.sale_order.order_line.tax_id = [Command.clear()]

    def test_copy_write(self):
        new_program = self.program.copy({"bankayma_discount_name": "Test program2"})
        self.assertEqual(new_program.reward_ids.description, "Test program2")
        new_program.bankayma_discount_name = "Test program3"
        self.assertEqual(new_program.reward_ids.description, "Test program3")

    def test_sale_order_global(self):
        so = self.sale_order
        self.program.bankayma_program_type = "promo_code_ou"
        new_program = self.program.copy(
            {
                "operating_unit_id": self.env.ref(
                    "operating_unit.b2b_operating_unit"
                ).id,
            }
        )
        new_program.bankayma_promo_code = "TEST00043"
        new_program.bankayma_discount_value = 25
        self.assertEqual(so.amount_total, 4284)
        code_result = so._try_apply_code("TEST00042")
        for coupon, reward in code_result.items():
            so._apply_program_reward(reward, coupon)
        # 20% applied to products of OU b2c
        self.assertEqual(so.amount_total, 4284 - 42 * 0.2)
        code_result = so._try_apply_code("TEST00043")
        for coupon, reward in code_result.items():
            so._apply_program_reward(reward, coupon)
        # new coupon overwrites old one, 25% applied to products of OU b2b
        self.assertEqual(so.amount_total, 4284 - 4242 * 0.25)

    def test_sale_order_product(self):
        so = self.sale_order
        self.program.bankayma_program_type = "promo_code_product"
        self.program.bankayma_product_ids = self.env.ref(
            "bankayma_website_sale.product_b2c"
        )
        self.assertEqual(so.amount_total, 4284)
        code_result = so._try_apply_code("TEST00042")
        for coupon, reward in code_result.items():
            so._apply_program_reward(reward, coupon)
        # 20% applied to product_b2c
        self.assertEqual(so.amount_total, 4284 - 42 * 0.2)

    def test_sale_order_product_multi(self):
        so = self.sale_order
        self.program.bankayma_program_type = "promo_code_product"
        self.program.bankayma_product_ids = self.env.ref(
            "bankayma_website_sale.product_b2c"
        )
        new_program = self.program.copy(
            {
                "operating_unit_id": self.env.ref(
                    "operating_unit.b2b_operating_unit"
                ).id,
            }
        )
        new_program.bankayma_product_ids = self.env.ref(
            "bankayma_website_sale.product_b2b"
        )
        new_program.bankayma_promo_code = "TEST00043"
        new_program.bankayma_discount_value = 25
        self.assertEqual(so.amount_total, 4284)
        code_result = so._try_apply_code("TEST00042")
        for coupon, reward in code_result.items():
            so._apply_program_reward(reward, coupon)
        code_result = so._try_apply_code("TEST00043")
        for coupon, reward in code_result.items():
            so._apply_program_reward(reward, coupon)
        # 20% applied to product_b2c, 25% applied to product_b2b
        self.assertAlmostEqual(so.amount_total, 4284 - 42 * 0.2 - 4242 * 0.25)
