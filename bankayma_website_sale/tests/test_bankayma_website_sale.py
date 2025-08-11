from odoo.fields import Command
from odoo.tests import common


class TestBankaymaWebsiteSale(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ref = cls.env.ref

        cls.product_b2b = ref("bankayma_website_sale.product_b2b")
        cls.product_b2c = ref("bankayma_website_sale.product_b2c")
        cls.ou_b2b = ref("operating_unit.b2b_operating_unit")
        cls.ou_b2c = ref("operating_unit.b2c_operating_unit")

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env["res.partner"]
                .search([], order="id desc", limit=1)
                .id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_b2b.id,
                            "product_uom_qty": 3,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_b2c.id,
                            "product_uom_qty": 10,
                        }
                    ),
                ],
            }
        )
        cls.bank_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("company_id", "=", cls.order.company_id.id),
            ]
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("company_id", "=", cls.order.company_id.id),
            ]
        )
        cls.sale_journal.bankayma_charge_overhead = True
        cls.env.company.overhead_account_id = cls.env["account.account"].create(
            {
                "name": "Overhead",
                "code": "4242420",
            }
        )
        cls.payment_provider = cls.env.ref("l10n_il_sumit.payment_provider_sumit")
        cls.payment_method = cls.env.ref("payment.payment_method_card")

    def _pay_order(self, order):
        transaction = self.env["payment.transaction"].create(
            {
                "sale_order_ids": [(6, 0, order.ids)],
                "provider_id": self.payment_provider.id,
                "payment_method_id": self.payment_method.id,
                "amount": order.amount_total,
                "partner_id": order.partner_id.id,
                "currency_id": order.currency_id.id,
                "state": "done",
                "operation": "online_redirect",
            }
        )
        transaction._post_process()

    def test_order_invoicing_single_ou(self):
        self.order.order_line[0].unlink()
        self.order.action_confirm()
        self._pay_order(self.order)
        invoices = self.order.invoice_ids
        self.assertEqual(invoices.operating_unit_id, self.ou_b2c)
        invoice_lines = invoices.invoice_line_ids
        self.assertEqual(invoice_lines.operating_unit_id, self.ou_b2c)
        self.assertAlmostEqual(
            invoice_lines.bankayma_parent_move_line_id.move_id.amount_total,
            0.07 * self.order.amount_total,
        )

    def test_order_invoicing_multi_ou(self):
        self.order.action_confirm()
        self._pay_order(self.order)
        invoices = self.order.invoice_ids
        self.assertFalse(invoices.operating_unit_id)
        invoice_lines = invoices.invoice_line_ids
        invoice_lines_b2b = invoice_lines.filtered(
            lambda x: x.product_id == self.product_b2b
        )
        self.assertEqual(invoice_lines_b2b.operating_unit_id, self.ou_b2b)
        invoice_lines_b2c = invoice_lines.filtered(
            lambda x: x.product_id == self.product_b2c
        )
        self.assertEqual(invoice_lines_b2c.operating_unit_id, self.ou_b2c)
        self.assertAlmostEqual(
            sum(
                invoice_lines.bankayma_parent_move_line_id.move_id.mapped(
                    "amount_total"
                )
            ),
            0.07 * self.order.amount_total,
        )
