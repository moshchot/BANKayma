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
        cls.bill = cls.env.ref("account.1_demo_invoice_5").copy(
            {
                "date": "2023-10-10",
                "invoice_date": "2023-10-10",
                "fiscal_position_id": cls.env.ref(
                    "bankayma_account.fpos_tax_deduction_artist"
                ).id,
            }
        )
        cls.custom_tax = cls.bill._portal_get_or_create_tax(
            cls.bill.company_id, cls.bill.fiscal_position_id, 41
        )
        cls.bill.invoice_line_ids.write(
            {
                "tax_ids": [Command.set(cls.custom_tax.ids)],
            }
        )

    def _import_file_valid(self, move_id):
        # TODO: just implement a writer for System1000File
        return b64encode(
            (
                "Airrelevant\r\n"
                "B{:>15}taxidsentvatidsenttaxidrecvvatidrecv                  name"
                "14200000000202301012023123120231230XXX1234567899999999999111111111\r\n"
                "Zirrelevant\r\n"
            )
            .format(self.bill.id)
            .encode(System1000File.encoding)
        )

    def test_import_valid_file_new_tax(self):
        """
        Test that we generate new taxes on the fly and replace the existing specific tax
        with it
        """
        wizard = self.env["l10n.il.system1000.export"].create(
            {
                "export_file": b64encode(b"irrelevant"),
                "import_file_valid": self._import_file_valid(self.bill.id),
            }
        )
        wizard.button_import()
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
        wizard = self.env["l10n.il.system1000.export"].create(
            {
                "export_file": b64encode(b"irrelevant"),
                "import_file_valid": self._import_file_valid(self.bill.id),
            }
        )
        wizard.button_import()
        self.assertEqual(self.bill.state, "posted")
