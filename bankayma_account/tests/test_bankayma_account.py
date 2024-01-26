# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions
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
        cls.parent.invoice_auto_validation = False
        cls.parent.intercompany_sale_journal_id = cls.env["account.journal"].create(
            {
                "name": "Intercompany sales",
                "code": "INS",
                "type": "sale",
                "company_id": cls.parent.id,
                "sequence": 100,
                "bankayma_restrict_partner": "intercompany",
            }
        )
        cls.parent.intercompany_purchase_journal_id = cls.env["account.journal"].create(
            {
                "name": "Intercompany purchases",
                "code": "INP",
                "type": "purchase",
                "company_id": cls.parent.id,
                "sequence": 100,
                "bankayma_restrict_partner": "intercompany",
            }
        )
        cls.parent.overhead_journal_id = cls.env["account.journal"].create(
            {
                "name": "Overhead",
                "code": "OVH",
                "type": "sale",
                "company_id": cls.parent.id,
                "sequence": 200,
                "bankayma_restrict_partner": "intercompany",
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
        cls.env["account.journal"].search(
            [("company_id", "=", cls.parent.id), ("type", "=", "sale")], limit=1
        ).write(
            {
                "bankayma_charge_overhead": True,
                "bankayma_restrict_partner": "no_intercompany",
            }
        )
        bank_account_wizard = (
            cls.env["account.setup.bank.manual.config"]
            .with_company(cls.parent)
            .create(
                {
                    "acc_number": "424242",
                    "new_journal_name": "424242",
                    "linked_journal_id": False,
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
                                cls.env.ref("bankayma_base.group_manager").id,
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
                                cls.env.ref("bankayma_base.group_manager").id,
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
        invoice_child1._bankayma_pay()
        invoice_child2._bankayma_pay()
        overhead_invoices = self.env["account.move"].search(
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
        self.assertEqual(
            overhead_invoices.mapped("journal_id"), self.parent.overhead_journal_id
        )
        self.assertItemsEqual(
            overhead_invoices.mapped("invoice_line_ids.name"),
            [
                "%s %s" % (invoice_child1.name, invoice_child1.partner_id.name),
                "%s %s" % (invoice_child2.name, invoice_child2.partner_id.name),
            ],
        )
        self.assertIn(
            self.parent.overhead_account_id,
            overhead_invoices.mapped("line_ids.account_id"),
        )
        child_overhead_invoices = overhead_invoices.mapped("auto_invoice_ids")
        self.assertEqual(
            child_overhead_invoices.mapped("need_validation"), [False, False]
        )
        self.assertEqual(
            child_overhead_invoices.mapped("payment_state"), ["paid", "paid"]
        )
        self.assertItemsEqual(
            child_overhead_invoices.mapped("journal_id"),
            self.child1.intercompany_purchase_journal_id
            + self.child2.intercompany_purchase_journal_id,
        )
        self.assertItemsEqual(
            child_overhead_invoices.mapped("invoice_line_ids.name"),
            [
                "%s %s" % (invoice_child1.name, invoice_child1.partner_id.name),
                "%s %s" % (invoice_child2.name, invoice_child2.partner_id.name),
            ],
        )
        draft_invoice = self._create_invoice(self.child1, self.user_child1)
        draft_invoice.with_context(force_delete=True).button_cancel_unlink()

    def _create_invoice(
        self, company, user, partner=None, post=True, extra_context=None
    ):
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .with_company(company)
            .with_context(default_move_type="out_invoice", **(extra_context or {}))
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

    def test_constraints(self):
        with self.assertRaises(exceptions.ValidationError):
            self.parent.overhead_payment_journal_id.bankayma_charge_overhead = True

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
        invoice_child2 = self.env["account.move"].search(
            [("auto_invoice_id", "=", invoice_child1.id)]
        )
        self.assertEqual(
            self.child1.intercompany_sale_journal_id, invoice_child1.journal_id
        )
        self.assertEqual(
            self.child2.intercompany_purchase_journal_id,
            invoice_child2.journal_id,
        )
        invoice_child2_as_child2 = invoice_child2.with_user(self.user_child2)
        invoice_child2_as_child2.review_ids.invalidate_model()
        self.assertEqual(invoice_child2.validated_state, "needs_validation")
        self.assertTrue(invoice_child2_as_child2.need_validation)
        self.assertTrue(invoice_child2_as_child2.can_review)
        invoice_child2_as_child2.validate_tier()
        self.assertEqual(invoice_child1.payment_state, "paid")
        self.assertEqual(invoice_child2.payment_state, "paid")
        invoice_child1 = invoice_child1.copy()
        self.assertEqual(invoice_child1.validated_state, "draft")
        invoice_child1.action_post()
        invoice_child2 = self.env["account.move"].search(
            [("auto_invoice_id", "=", invoice_child1.id)]
        )
        invoice_child2_as_child2 = invoice_child2.with_user(self.user_child2)
        invoice_child2_as_child2.review_ids.invalidate_model()
        self.assertTrue(invoice_child2_as_child2.need_validation)
        self.assertTrue(invoice_child2_as_child2.can_review)
        self.env.ref(
            "bankayma_account.tier_definition_intercompany_purchase"
        ).has_comment = False
        invoice_child2_as_child2.reject_tier()
        self.assertEqual(invoice_child1.state, "draft")
        self.assertEqual(invoice_child2.state, "cancel")

    def test_same_sequence(self):
        journal_parent = self.env["account.journal"].create(
            {
                "name": "Test sale journal",
                "code": "JNL",
                "type": "sale",
                "company_id": self.parent.id,
                "sequence_id": self.env["ir.sequence"]
                .create(
                    {
                        "name": "Shared sequence",
                        "prefix": "shared",
                        "padding": 5,
                        "company_id": False,
                    }
                )
                .id,
            }
        )
        journal_parent.refund_sequence_id._company_cascade()
        journal_parent._company_cascade()
        journal_child1 = journal_parent.company_cascade_child_ids.filtered(
            lambda x: x.company_id == self.child1
        )
        journal_child2 = journal_parent.company_cascade_child_ids.filtered(
            lambda x: x.company_id == self.child2
        )
        self.assertEqual(journal_parent.sequence_id, journal_child1.sequence_id)
        self.assertEqual(journal_child1.sequence_id, journal_child2.sequence_id)
        invoice_parent = self._create_invoice(
            self.parent,
            self.env.user,
            extra_context={"default_journal_id": journal_parent.id},
        )
        invoice_child1 = self._create_invoice(
            self.child1,
            self.user_child1,
            extra_context={"default_journal_id": journal_child1.id},
        )
        invoice_child2 = self._create_invoice(
            self.child2,
            self.user_child2,
            extra_context={"default_journal_id": journal_child2.id},
        )
        self.assertEqual(invoice_parent.name, "shared00001")
        self.assertEqual(invoice_child1.name, "shared00002")
        self.assertEqual(invoice_child2.name, "shared00003")
        invoice_parent = self._create_invoice(
            self.parent,
            self.env.user,
            extra_context={"default_journal_id": journal_parent.id},
        )
        self.assertEqual(invoice_parent.name, "shared00004")

    def test_individual_il_vat(self):
        """Test that the system accepts vats from individials in IL"""
        partner = self.env["res.partner"].create(
            {
                "name": "individual",
                "country_id": self.env.ref("base.il").id,
                "is_company": False,
            }
        )
        partner.vat = "555"
