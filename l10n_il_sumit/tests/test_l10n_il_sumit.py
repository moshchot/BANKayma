# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestL10nIlSumit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.env["account.move"].search(
            [("move_type", "=", "out_invoice")], limit=1
        )

    def test_sumit_vals(self):
        """Test we translate Odoo objects to sumit correctly"""
        sumit_vals = self.invoice._to_sumit_vals()
        # TODO: add much more assertions
        self.assertEqual(
            sumit_vals["Details"]["Type"], self.invoice.journal_id.sumit_type
        )
