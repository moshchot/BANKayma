# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase
from odoo.tools.misc import mute_logger


class TestBankaymaAccount(TransactionCase):
    @classmethod
    @mute_logger(
        "odoo.models.unlink", "odoo.addons.mail.models.mail_mail", "odoo.tests"
    )
    def setUpClass(cls):
        super().setUpClass()
        Wizard = cls.env["bankayma.company.create"]
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.parent = cls.env.ref("bankayma_base.child_comp1")
        if not cls.parent.chart_template_id:
            cls.env.ref("l10n_il.il_chart_template").try_loading(cls.parent)
        if not cls.parent.country_id:
            cls.parent.country_id = cls.env.ref("base.il")
        cls.parent.code = "4242"
        cls.parent.intercompany_sale_journal_id = cls.env["account.journal"].create(
            {
                "name": "Intercompany sales",
                "code": "INS",
                "type": "sale",
                "company_id": cls.parent.id,
                "sequence": 100,
            }
        )
        cls.parent.intercompany_purchase_journal_id = cls.env["account.journal"].create(
            {
                "name": "Intercompany purchases",
                "code": "INP",
                "type": "purchase",
                "company_id": cls.parent.id,
                "sequence": 100,
            }
        )
        cls.parent.overhead_journal_id = cls.env["account.journal"].create(
            {
                "name": "Overhead",
                "code": "OVH",
                "type": "sale",
                "company_id": cls.parent.id,
                "sequence": 200,
            }
        )
        cls.parent.overhead_account_id = cls.env["account.account"].create(
            {
                "name": "Overhead",
                "company_id": cls.parent.id,
                "code": "4242420",
            }
        )
        cls.parent.overhead_payment_journal_id = cls.env["account.journal"].create(
            {
                "name": "Overhead Payments",
                "code": "OVHP",
                "type": "bank",
                "company_id": cls.parent.id,
                "sequence": 200,
            }
        )
        bank_account_wizard = (
            cls.env["account.setup.bank.manual.config"]
            .with_company(cls.parent)
            .create(
                {
                    "acc_number": "424242",
                    "new_journal_name": "424242",
                    "bank_id": None,
                    "bank_bic": None,
                }
            )
        )
        cls.parent_bank_account = bank_account_wizard.res_partner_bank_id
        cls.parent_bank_journal = bank_account_wizard.linked_journal_id
        cls.child1 = Wizard._create_company(cls.parent, "child1", "ch1")
        cls.user_child1 = (
            Users.sudo()
            .with_company(cls.child1)
            .create(
                {
                    "name": "user_child1",
                    "login": "user_child1",
                    "email": "user@child1",
                    "company_id": cls.child1.id,
                    "company_ids": [Command.set(cls.child1.ids)],
                    "groups_id": [
                        Command.set(
                            [
                                cls.env.ref("account.group_account_invoice").id,
                                cls.env.ref("bankayma_base.group_user").id,
                            ]
                        )
                    ],
                }
            )
        )
        cls.child2 = Wizard._create_company(cls.parent, "child2", "ch2")
        cls.user_child2 = (
            Users.sudo()
            .with_company(cls.child2)
            .create(
                {
                    "name": "user_child2",
                    "login": "user_child2",
                    "email": "user@child2",
                    "company_id": cls.child2.id,
                    "company_ids": [Command.set(cls.child2.ids)],
                    "groups_id": [
                        Command.set(
                            [
                                cls.env.ref("account.group_account_invoice").id,
                                cls.env.ref("bankayma_base.group_user").id,
                            ]
                        )
                    ],
                }
            )
        )
        cls.product = (
            cls.env["product.product"]
            .with_company(cls.parent)
            .create({"name": "Testproduct", "sale_ok": True, "lst_price": 42})
        )

    def test_basic_function(self):
        invoice_child1 = self._create_invoice(self.child1, self.user_child1)
        invoice_child2 = self._create_invoice(self.child2, self.user_child2)
        self.assertEqual(invoice_child2.mapped("line_ids.company_id"), self.child2)
        self.assertEqual(
            invoice_child2.mapped("line_ids.account_id.company_id"), self.child2
        )
        self.assertEqual(invoice_child2.mapped("line_ids.product_id"), self.product)
        self.assertEqual(
            invoice_child2.mapped("line_ids.tax_ids.company_id"), self.child2
        )
        self.assertEqual(invoice_child2.amount_untaxed, 84)
        self.assertNotEqual(invoice_child1.name, invoice_child2.name)
        self.assertTrue(self.parent.account_journal_payment_debit_account_id)
        self.assertTrue(self.child1.account_journal_payment_debit_account_id)
        self.assertTrue(self.child2.account_journal_payment_debit_account_id)
        self.assertNotEqual(
            self.parent.account_journal_payment_debit_account_id,
            self.child1.account_journal_payment_debit_account_id,
        )
        self.assertNotEqual(
            self.parent.account_journal_payment_debit_account_id,
            self.child2.account_journal_payment_debit_account_id,
        )
        self.assertNotEqual(
            self.child1.account_journal_payment_debit_account_id,
            self.child2.account_journal_payment_debit_account_id,
        )
        self._pay_invoice(invoice_child1)
        self._pay_invoice(invoice_child2)
        invoices = self.env["account.move"].search(
            [
                (
                    "line_ids",
                    "in",
                    (invoice_child1 + invoice_child2)
                    .sudo()
                    .mapped("line_ids.bankayma_parent_move_line_id")
                    .ids,
                )
            ]
        )
        self.assertEqual(invoices.mapped("journal_id"), self.parent.overhead_journal_id)
        self.assertIn(
            self.parent.overhead_account_id, invoices.mapped("line_ids.account_id")
        )
        child_invoices = self.env["account.move"].search(
            [("auto_invoice_id", "in", invoices.ids)]
        )
        self.assertEqual(child_invoices.mapped("payment_state"), ["paid", "paid"])
        self.assertItemsEqual(
            self.env["account.move"]
            .search([("auto_invoice_id", "in", invoices.ids)])
            .mapped("journal_id")
            .ids,
            (
                self.child1.intercompany_purchase_journal_id
                + self.child2.intercompany_purchase_journal_id
            ).ids,
        )
        draft_invoice = self._create_invoice(self.child1, self.user_child1)
        draft_invoice.button_cancel_unlink()

    def _create_invoice(self, company, user, partner=None, post=True):
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .with_company(company)
            .with_context(default_move_type="out_invoice")
            .create({})
        )
        partner = partner or (
            self.env["res.partner"]
            .with_user(user)
            .with_company(company)
            .search([], limit=1)
        )
        product = self.product.with_company(company)
        with Form(invoice, view="account.view_move_form") as invoice_form:
            invoice_form.partner_id = partner
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = product
                line.quantity = 2
        if post:
            if invoice.need_validation:
                invoice.sudo().validate_tier()
            invoice.action_post()
        return invoice

    def _pay_invoice(self, invoice):
        action = invoice.action_register_payment()
        with Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ) as payment_form:
            payment = payment_form.save()
        payment.action_create_payments()

    def test_cascade(self):
        account = self.env["account.account"].search(
            [("company_id", "=", self.child1.id)], limit=1
        )
        original_code = account.code
        parent_account = account.company_cascade_parent_id
        self.parent.code = "4242"
        self.child1.code = "4343"
        parent_account.code = "4242X" + parent_account.code
        parent_account._company_cascade()
        self.assertEqual(account.code, "4343X" + original_code)
        child1_bank_account = self.child1.partner_id.bank_ids
        child2_bank_account = self.child2.partner_id.bank_ids
        self.assertEqual(child1_bank_account.acc_number, "424242")
        self.assertEqual(child2_bank_account.acc_number, "424242")
        self.assertEqual(
            self.child1.account_journal_payment_debit_account_id.company_cascade_parent_id,
            self.parent.account_journal_payment_debit_account_id,
        )
        self.assertEqual(
            set(
                self.parent_bank_journal.mapped(
                    "outbound_payment_method_line_ids"
                ).mapped(lambda x: (x.name, x.code, x.payment_type))
            ),
            set(
                self.parent_bank_journal.mapped(
                    "company_cascade_child_ids.outbound_payment_method_line_ids"
                ).mapped(lambda x: (x.name, x.code, x.payment_type))
            ),
        )

    def test_intercompany(self):
        invoice_child1 = self._create_invoice(
            self.child1, self.user_child1, self.child2.partner_id
        )
        invoice_child1_inverse = self.env["account.move"].search(
            [("auto_invoice_id", "=", invoice_child1.id)]
        )
        invoice_child2 = self._create_invoice(
            self.child2, self.user_child2, self.child1.partner_id
        )
        invoice_child2_inverse = self.env["account.move"].search(
            [("auto_invoice_id", "=", invoice_child2.id)]
        )
        self.assertEqual(
            self.child1.intercompany_sale_journal_id, invoice_child1.journal_id
        )
        self.assertEqual(
            self.child2.intercompany_purchase_journal_id,
            invoice_child1_inverse.journal_id,
        )
        self.assertEqual(
            self.child2.intercompany_sale_journal_id, invoice_child2.journal_id
        )
        self.assertEqual(
            self.child1.intercompany_purchase_journal_id,
            invoice_child2_inverse.journal_id,
        )
