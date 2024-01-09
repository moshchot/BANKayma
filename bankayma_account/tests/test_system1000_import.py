# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo.fields import Command
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_il_system1000.system1000_file import System1000File


class TestSystem1000Import(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("bankayma_account.tier_definition_vendor_bill").active = True
        cls.bill = (
            cls.env.ref("account.1_demo_invoice_5")
            .copy(
                {
                    "date": "2023-10-10",
                    "invoice_date": "2023-10-10",
                    "fiscal_position_id": cls.env.ref(
                        "bankayma_account.fpos_tax_deduction_artist"
                    ).id,
                }
            )
            .with_user(cls.env.ref("base.user_admin"))
        )
        cls.custom_tax = cls.bill._portal_get_or_create_tax(
            cls.bill.company_id, cls.bill.fiscal_position_id, 41
        )
        cls.bill.invoice_line_ids.write(
            {
                "tax_ids": [Command.set(cls.custom_tax.ids)],
            }
        )

    def _import_file_valid(self, move_id, from_date="20230101", to_date="20231231"):
        # TODO: just implement a writer for System1000File
        return b64encode(
            (
                "Airrelevant\r\n"
                "B{:>15}taxidsentvatidsenttaxidrecvvatidrecv                  name"
                "14200000000{:>8}{:>8}20231230XXX1234567899999999999111111111\r\n"
                "Zirrelevant\r\n"
            )
            .format(self.bill.id, from_date, to_date)
            .encode(System1000File.encoding)
        )

    def _run_import(self, **wizard_kwargs):
        """Run the wizard and return it"""
        create_args = {}
        create_args.update(export_file=b64encode(b"irrelevant"))
        create_args.update(**(wizard_kwargs or {}))
        wizard = self.bill.env["l10n.il.system1000.export"].create(create_args)
        wizard.button_import()
        return wizard

    def test_import_valid_file_out_of_date(self):
        """
        Test that we generate new taxes on the fly and replace the existing specific tax
        with it
        """
        self.bill.date = "2024-01-01"
        self._run_import(import_file_valid=self._import_file_valid(self.bill.id))
        self.assertEqual(self.bill.state, "cancel")

    def test_import_valid_file_new_tax(self):
        """
        Test that we generate new taxes on the fly and replace the existing specific tax
        with it
        """
        self._run_import(import_file_valid=self._import_file_valid(self.bill.id))
        self.assertIn(
            self.bill.fiscal_position_id.bankayma_deduct_tax_group_id,
            self.bill.mapped("invoice_line_ids.tax_ids.tax_group_id"),
        )
        self.assertNotIn(self.custom_tax, self.bill.mapped("invoice_line_ids.tax_ids"))

    def test_import_valid_file_auto_confirm(self):
        """Test that we confirm moves when everything matches"""
        custom_tax = self.bill._portal_get_or_create_tax(
            self.bill.company_id, self.bill.fiscal_position_id, 42
        )
        self.bill.invoice_line_ids.write(
            {
                "tax_ids": [Command.set(custom_tax.ids)],
            }
        )
        self._run_import(import_file_valid=self._import_file_valid(self.bill.id))
        self.assertEqual(self.bill.state, "posted")

    def test_import_valid_file_auto_confirm_no_tier_validation(self):
        """Test that we confirm moves when everything matches without tier validation"""
        self.env["tier.definition"].search([]).write({"active": False})
        self.test_import_valid_file_auto_confirm()

    def test_import_valid_file_nondraft(self):
        """Test that ignore moves that aren't in draft state"""
        self.bill.button_cancel()
        self._run_import(import_file_valid=self._import_file_valid(self.bill.id))
        self.assertEqual(self.bill.state, "cancel")

    def test_import_valid_file_auto_confirm_tier_validation_running(self):
        """Test that we confirm moves when everything matches without tier validation"""
        self.bill.with_user(self.env.ref("base.user_demo")).request_validation()
        self.bill.invalidate_recordset()
        self.test_import_valid_file_auto_confirm()

    def test_import_invalid_file(self):
        """Test that we autoreject invalid files"""
        self.bill.with_user(self.env.ref("base.user_demo")).request_validation()
        self.bill.invalidate_recordset()
        wizard = self.env["l10n.il.system1000.export"].create(
            {
                "export_file": b64encode(b"irrelevant"),
                "import_file_invalid": self._import_file_valid(self.bill.id),
            }
        )
        wizard.button_import()
        self.assertEqual(self.bill.state, "cancel")
