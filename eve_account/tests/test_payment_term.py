from odoo.tests.common import Form, TransactionCase


class TestPaymentTerm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["tier.definition"].search([]).write({"active": False})
        cls.term = cls.env["account.payment.term"].create(
            {
                "name": "fixed date",
            }
        )
        with Form(cls.term) as payment_term_form:
            payment_term_form.fixed_date = "2020-06-01"
        cls.invoice = (
            cls.env["account.move"]
            .with_context(default_move_type="in_invoice")
            .create(
                {
                    "partner_id": cls.env["res.partner"].search([], limit=1).id,
                    "invoice_date": "2020-05-23",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "/",
                                "price_unit": 42,
                            },
                        )
                    ],
                    "invoice_payment_term_id": cls.term.id,
                }
            )
        )

    def test_payment_term(self):
        self.invoice.action_post()
        self.assertEqual(
            self.invoice.line_ids.filtered("date_maturity").date_maturity,
            self.term.fixed_date,
        )
