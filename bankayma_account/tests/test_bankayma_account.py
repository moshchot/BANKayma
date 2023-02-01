# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase
from odoo.tools.misc import mute_logger


class TestBankaymaAccount(TransactionCase):
    @mute_logger(
        "odoo.models.unlink", "odoo.addons.mail.models.mail_mail", "odoo.tests"
    )
    def setUp(self):
        super().setUp()
        Wizard = self.env["bankayma.company.create"]
        Users = self.env["res.users"].with_context(no_reset_password=True)
        self.parent = self.env.ref("bankayma_base.child_comp1")
        if not self.parent.chart_template_id:
            self.env.ref("l10n_il.il_chart_template").try_loading(self.parent)
        if not self.parent.country_id:
            self.parent.country_id = self.env.ref("base.il")
        self.parent.code = "4242"
        self.parent.intercompany_sale_journal_id = self.env["account.journal"].create(
            {
                "name": "Intercompany sales",
                "code": "INS",
                "type": "sale",
                "company_id": self.parent.id,
                "sequence": 100,
            }
        )
        self.parent.intercompany_purchase_journal_id = self.env[
            "account.journal"
        ].create(
            {
                "name": "Intercompany purchases",
                "code": "INP",
                "type": "purchase",
                "company_id": self.parent.id,
                "sequence": 100,
            }
        )
        bank_account_wizard = (
            self.env["account.setup.bank.manual.config"]
            .with_company(self.parent)
            .create(
                {
                    "acc_number": "424242",
                    "new_journal_name": "424242",
                    "bank_id": None,
                    "bank_bic": None,
                }
            )
        )
        self.parent_bank_account = bank_account_wizard.res_partner_bank_id
        self.child1 = Wizard._create_company(self.parent, "child1", "ch1")
        self.user_child1 = (
            Users.sudo()
            .with_company(self.child1)
            .create(
                {
                    "name": "user_child1",
                    "login": "user_child1",
                    "company_id": self.child1.id,
                    "company_ids": [Command.set(self.child1.ids)],
                    "groups_id": [
                        Command.set(
                            [
                                self.env.ref("account.group_account_invoice").id,
                                self.env.ref("bankayma_base.group_user").id,
                            ]
                        )
                    ],
                }
            )
        )
        self.child2 = Wizard._create_company(self.parent, "child2", "ch2")
        self.user_child2 = (
            Users.sudo()
            .with_company(self.child2)
            .create(
                {
                    "name": "user_child2",
                    "login": "user_child2",
                    "company_id": self.child2.id,
                    "company_ids": [Command.set(self.child2.ids)],
                    "groups_id": [
                        Command.set(
                            [
                                self.env.ref("account.group_account_invoice").id,
                                self.env.ref("bankayma_base.group_user").id,
                            ]
                        )
                    ],
                }
            )
        )
        self.product = (
            self.env["product.product"]
            .with_company(self.parent)
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
            invoice.action_post()
        return invoice

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
