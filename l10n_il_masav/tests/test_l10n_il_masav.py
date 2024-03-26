from base64 import b64decode

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestL10nIlMasav(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref("base.user_admin")
        cls.user.company_id = cls.env.ref("l10n_il.demo_company_il")
        cls.user.company_id.vat = "IL516179157"

    def _test_export(self, moves):
        wizard = (
            self.env["l10n.il.masav.export"]
            .with_user(self.user)
            .with_company(self.user.company_id)
            .with_context(active_ids=moves.ids)
            .create({})
        )
        wizard.button_export()
        export_data = b64decode(wizard.export_file).decode("iso8859-8").splitlines()
        self.assertTrue(export_data[-1].startswith("9"))

    def _amend_partners(self, moves):
        for partner in moves.mapped("partner_id"):
            partner.write(
                {
                    "bank_ids": [
                        (5, False, False),
                        (
                            0,
                            0,
                            {
                                "bank_id": self.env.ref("l10n_il_bank.bank_4").id,
                                "acc_number": "4242424",
                                "branch_code": "42",
                            },
                        ),
                    ],
                    "vat": "IL516179157",
                }
            )

    def test_export(self):
        moves = self.env["account.move"].search(
            [
                ("move_type", "=", "in_invoice"),
                ("company_id", "=", self.user.company_id.id),
                ("state", "=", "posted"),
            ]
        )

        with self.assertRaisesRegex(
            exceptions.UserError, "is missing bank account information"
        ):
            self._test_export(moves)
        self._amend_partners(moves)
        self._test_export(moves)

        moves = self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("company_id", "=", self.user.company_id.id),
            ]
        )
        with self.assertRaisesRegex(exceptions.UserError, "vendor bills"):
            self._test_export(moves)

        moves = self.env["account.move"].search([("move_type", "=", "in_invoice")])
        self.user.company_ids = moves.mapped("company_id")
        with self.assertRaisesRegex(exceptions.UserError, "same company"):
            self._test_export(moves)

        moves = self.env["account.move"].search(
            [
                ("move_type", "=", "in_invoice"),
                ("company_id", "=", self.user.company_id.id),
                ("state", "=", "draft"),
            ]
        )
        with self.assertRaisesRegex(exceptions.UserError, "posted bills"):
            self._test_export(moves)
