# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
from unittest.mock import patch

from odoo import exceptions
from odoo.fields import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger

USER_FILE_TEMPLATE = """empty,line
empty,line
empty,line
%(ou_code)s,%(ou_name)s,%(function)s,%(login)s,%(name)s,%(email)s,%(phone)s
"""


class TestBankaymaAccount(TransactionCase):
    @classmethod
    @mute_logger(
        "odoo.models.unlink", "odoo.addons.mail.models.mail_mail", "odoo.tests"
    )
    def setUpClass(cls):
        super().setUpClass()
        Wizard = cls.env["bankayma.ou.create"]
        cls.parent = cls.env.ref("operating_unit.main_operating_unit")
        cls.child1 = Wizard._create_ou(cls.parent, "child1", "CH1")
        cls.child2 = Wizard._create_ou(cls.parent, "child2", "CH2")

        Wizard.create(
            {
                "template_operating_unit_id": cls.parent.id,
                "user_file": base64.b64encode(
                    (
                        USER_FILE_TEMPLATE
                        % {
                            "ou_code": "CH1",
                            "ou_name": "child1",
                            "function": "Function User child 1",
                            "login": "user_child1",
                            "name": "User child 1",
                            "email": "user@child1",
                            "phone": "42424242-1",
                        }
                    ).encode("utf8")
                ),
            }
        ).action_create()
        cls.user_child1 = cls.env["res.users"].search([("login", "=", "user_child1")])

        Wizard.create(
            {
                "template_operating_unit_id": cls.parent.id,
                "ou_code": "CH2",
                "ou_name": "child2",
                "user_function": "Function User child 2",
                "user_login": "user_child2",
                "user_name": "User child 2",
                "user_email": "user@child2",
                "user_phone": "42424242-2",
            }
        ).action_create()
        cls.user_child2 = cls.env["res.users"].search([("login", "=", "user_child2")])

        cls.env.company.overhead_journal_id = cls.env["account.journal"].create(
            {
                "name": "Overhead",
                "code": "OVH",
                "type": "sale",
                "sequence": 200,
                "bankayma_restrict_partner": "intercompany",
            }
        )
        cls.env.company.overhead_account_id = cls.env["account.account"].create(
            {
                "name": "Overhead",
                "code": "4242420",
            }
        )
        cls.env.company.overhead_payment_journal_id = cls.env["account.journal"].create(
            {
                "name": "Overhead Payments",
                "code": "OVHP",
                "type": "bank",
                "sequence": 200,
            }
        )
        cls.env["account.journal"].search([("type", "=", "sale")], limit=1).write(
            {
                "bankayma_charge_overhead": True,
                "bankayma_restrict_partner": "no_intercompany",
            }
        )
        bank_account_wizard = (
            cls.env["account.setup.bank.manual.config"]
            .with_ou(cls.parent)
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
        bank_account_wizard._compute_linked_journal_id()
        cls.parent_bank_account = bank_account_wizard.res_partner_bank_id
        cls.parent_bank_journal = bank_account_wizard.linked_journal_id
        cls.product = cls.env["product.product"].create(
            {"name": "Testproduct", "sale_ok": True, "lst_price": 42}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic account",
                "plan_id": cls.env["account.analytic.plan"]
                .create(
                    {
                        "name": "Plan without company",
                    }
                )
                .id,
            }
        )

    def test_basic_function(self):
        invoice_child1 = self._create_invoice(self.child1, self.user_child1)
        invoice_child2 = self._create_invoice(self.child2, self.user_child2)
        self.assertEqual(
            invoice_child2.mapped("line_ids.operating_unit_id"), self.child2
        )
        self.assertEqual(invoice_child2.mapped("line_ids.product_id"), self.product)
        self.assertEqual(invoice_child2.amount_untaxed, 84)
        self.assertNotEqual(invoice_child1.name, invoice_child2.name)
        (invoice_child1 + invoice_child2).with_user(self.env.user)._bankayma_pay()
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
            overhead_invoices.mapped("journal_id"), self.env.company.overhead_journal_id
        )
        self.assertItemsEqual(
            overhead_invoices.mapped("invoice_line_ids.name"),
            [
                f"{invoice_child1.name} {invoice_child1.partner_id.name}",
                f"{invoice_child1.name} {invoice_child1.partner_id.name}",
                f"{invoice_child2.name} {invoice_child2.partner_id.name}",
                f"{invoice_child2.name} {invoice_child2.partner_id.name}",
            ],
        )
        self.assertIn(
            self.env.company.overhead_account_id,
            overhead_invoices.mapped("line_ids.account_id"),
        )
        self.assertItemsEqual(
            set(
                int(_id)
                for distribution in overhead_invoices.invoice_line_ids.mapped(
                    lambda x: x.analytic_distribution
                )
                for _id, _percentage in (distribution or {}).items()
            ),
            self.analytic_account.ids,
        )
        draft_invoice = self._create_invoice(self.child1, self.user_child1)
        draft_invoice.with_context(force_delete=True).button_cancel_unlink()
        invoice_child1_with_negative_line = self._create_invoice(
            self.child1, self.user_child1, post=False
        )
        with Form(
            invoice_child1_with_negative_line, view="account.view_move_form"
        ) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = self.product.with_ou(self.child1)
                line.name = "product line"
                line.quantity = 1
                line.price_unit = -10
        invoice_child1_with_negative_line.action_post()
        invoice_child1_with_negative_line.with_user(self.env.user)._bankayma_pay()

    def _create_invoice(self, ou, user, partner=None, post=True, extra_context=None):
        invoice = (
            self.env["account.move"]
            .with_ou(ou)
            .with_user(user)
            .with_context(default_move_type="out_invoice", **(extra_context or {}))
            .create({})
        )
        partner = partner or (
            self.env["res.partner"].with_user(user).with_ou(ou).search([], limit=1)
        )
        product = self.product.with_ou(ou)
        with Form(invoice, view="account.view_move_form") as invoice_form:
            invoice_form.partner_id = partner
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = product
                line.name = "product line"
                line.quantity = 2
                line.analytic_distribution = {self.analytic_account.id: 100}
        if post:
            if invoice.need_validation:
                invoice.sudo().validate_tier()
            invoice.action_post()
        return invoice

    def test_constraints(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env.company.overhead_payment_journal_id.bankayma_charge_overhead = True

    def _test_intercompany(self):
        # TODO: verify this
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
        self.assertEqual(invoice_child2.validated_state, "1_needs_validation")
        self.assertTrue(invoice_child2_as_child2.need_validation)
        self.assertTrue(invoice_child2_as_child2.can_review)
        invoice_child2_as_child2.validate_tier()
        self.assertEqual(invoice_child1.payment_state, "paid")
        self.assertEqual(invoice_child2.payment_state, "paid")
        invoice_child1 = invoice_child1.copy()
        self.assertEqual(invoice_child1.validated_state, "0_draft")
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
        invoice_parent = self._create_invoice(
            self.parent,
            self.env.user,
            extra_context={"default_journal_id": journal_parent.id},
        )
        invoice_child1 = self._create_invoice(
            self.child1,
            self.user_child1,
            extra_context={"default_journal_id": journal_parent.id},
        )
        invoice_child2 = self._create_invoice(
            self.child2,
            self.user_child2,
            extra_context={"default_journal_id": journal_parent.id},
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

    def test_change_fpos(self):
        """
        Test that changing the fiscal position on a move recalculates taxes
        """
        invoice = self._create_invoice(self.child1, self.user_child1, post=False)
        tax = self.env["account.tax"].create(
            {
                "name": "tax1",
            }
        )
        invoice.invoice_line_ids.tax_ids = tax.copy()
        fpos = self.env["account.fiscal.position"].create(
            {
                "name": "To tax1",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": invoice.invoice_line_ids.tax_ids.id,
                            "tax_dest_id": tax.id,
                        },
                    )
                ],
            }
        )
        invoice.fiscal_position_id = fpos
        self.assertEqual(invoice.invoice_line_ids.tax_ids, tax)
        fpos = self.env["account.fiscal.position"].create(
            {
                "name": "Remove tax",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": invoice.invoice_line_ids.tax_ids.id,
                        },
                    )
                ],
            }
        )
        invoice.fiscal_position_id = fpos
        self.assertFalse(invoice.invoice_line_ids.tax_ids)

    def test_change_provisioned_bank(self):
        """Test that we can only edit provisioned banks as superuser"""
        bank = self.env.ref("l10n_il_bank.bank_4")
        with self.assertRaises(exceptions.AccessError):
            bank.with_user(self.user_child1).name = "test"
        with self.assertRaises(exceptions.AccessError):
            bank.with_user(self.user_child1).unlink()
        bank.name = "test2"
        self.env.invalidate_all()
        self.assertEqual(bank.name, "test2")

    def test_change_operating_unit(self):
        """Test the operating unit change wizard"""
        self.user_child1.write(
            {
                "groups_id": [(4, self.env.ref("bankayma_base.group_manager").id)],
                "operating_unit_ids": [(4, self.child2.id)],
            }
        )
        invoice = self._create_invoice(self.child1, self.user_child1, post=False)
        self.assertEqual(invoice.operating_unit_id, self.child1)
        plan = self.env["account.analytic.plan"].create(
            {
                "name": "testplan",
            }
        )
        account = self.env["account.analytic.account"].create(
            {
                "name": "testaccount",
                "plan_id": plan.id,
            }
        )
        invoice.invoice_line_ids.analytic_distribution = {str(account.id): 100}
        original_amount = invoice.amount_total
        wizard = (
            self.env["bankayma.move.change.company"]
            .with_user(self.user_child1)
            .with_context(
                active_model=invoice._name,
                active_id=invoice.id,
                active_ids=invoice.ids,
            )
            .create({"operating_unit_id": self.child2.id})
        )
        wizard.action_change_operating_unit()
        self.assertEqual(invoice.operating_unit_id, self.child2)
        self.assertEqual(invoice.amount_total, original_amount)
        self.assertIn(str(account.id), invoice.invoice_line_ids.analytic_distribution)

    def test_delete(self):
        """
        Test that deletion works after cascading
        """
        self.child1.unlink()
        self.assertFalse(self.child1.exists())

    def test_sumit(self):
        """
        Test sumit specific functionality
        """
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        journal.use_sumit = True
        invoice = self._create_invoice(self.child1, self.user_child1)
        with patch.object(
            self.env["sumit.account"].__class__, "_request"
        ) as mock_request:
            mock_request.side_effect = lambda self, *args, **kwargs: {
                "DocumentNumber": 42,
                "DocumentDownloadURL": "",
            }
            invoice.sudo()._bankayma_pay(payment_comment="the payment communication")
        mock_request.assert_called()
        self.assertEqual(
            mock_request.call_args[0][1]["Details"]["Description"],
            "the payment communication",
        )
        invoice1 = self._create_invoice(self.child1, self.user_child1)
        invoice2 = self._create_invoice(self.child1, self.user_child1)
        with patch.object(
            self.env["sumit.account"].__class__, "_request"
        ) as mock_request:
            mock_request.side_effect = lambda self, *args, **kwargs: {
                "DocumentNumber": 42,
                "DocumentDownloadURL": "",
            }
            (invoice1 + invoice2).sudo()._bankayma_pay(
                payment_comment="the payment communication"
            )
        mock_request.assert_called()
        self.assertEqual(
            mock_request.call_args[0][1]["Details"]["Description"],
            "the payment communication",
        )

    def test_recurring_contract(self):
        """
        Test that invoices deriving from recurring contracts are reconciled with
        the invoices sumit creates, without creating new invoices on the sumit side
        """
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.child1.id)], limit=1
        )
        journal.use_sumit = True
        contract = (
            self.env["contract.contract"]
            .with_ou(self.child1)
            .create(
                {
                    "name": "Testcontract",
                    "journal_id": journal.id,
                    "sumit_details": {
                        "RecurringCustomerItemIDs": [424242],
                    },
                    "partner_id": self.env["res.partner"].search([], limit=1).id,
                    "contract_line_ids": [
                        Command.create(
                            {
                                "name": "Test contract line",
                                "date_start": "2026-01-01",
                                "price_unit": 42,
                            }
                        )
                    ],
                }
            )
        )
        invoice = contract._recurring_create_invoice()

        def sumit_request(endpoint, payload):
            if endpoint == "/billing/payments/list":
                if payload["StartIndex"] == 0:
                    return {
                        "Payments": [],
                        "HasNextPage": True,
                    }
                return {
                    "Payments": [
                        {
                            "RecurringCustomerItemIDs": contract.sumit_details[
                                "RecurringCustomerItemIDs"
                            ],
                            "Amount": invoice.amount_total,
                        }
                    ]
                }

        with patch.object(
            self.env["sumit.account"].__class__, "_request"
        ) as mock_request:
            mock_request.side_effect = sumit_request
            self.env["contract.contract"]._sumit_process_invoices()

        overhead_invoice = invoice.invoice_line_ids.bankayma_parent_move_line_id.move_id
        self.assertTrue(overhead_invoice)
        self.assertFalse(overhead_invoice.sumit_document_url)

        payment = (
            invoice.line_ids.full_reconcile_id.reconciled_line_ids.move_id.payment_id
        )
        self.assertEqual(
            payment.payment_method_line_id.code,
            "sumit_defrayal",
        )

        self.assertEqual(mock_request.call_count, 2)
        self.assertEqual(
            mock_request.call_args_list[0].args[0],
            "/billing/payments/list",
        )
        self.assertEqual(
            mock_request.call_args_list[1].args[0],
            "/billing/payments/list",
        )
