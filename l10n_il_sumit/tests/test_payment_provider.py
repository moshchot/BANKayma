# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from unittest.mock import Mock, patch

from odoo.tests import tagged

from odoo.addons.payment.tests.common import PaymentCommon

from ..models.sumit_account import requests


@tagged("-at_install", "post_install")
class TestPaymentProvider(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls._prepare_provider(
            "sumit",
            update_values={
                "sumit_account_id": cls.env["sumit.account"]
                .create(
                    {
                        "company_code": "424242",
                        "key": "key",
                    }
                )
                .id,
                "journal_id": cls.env["account.journal"]
                .search(
                    [
                        ("company_id", "=", cls.env.company.id),
                        ("type", "=", "bank"),
                    ],
                    limit=1,
                )
                .id,
            },
        )
        cls.invoice = cls.env.ref("account.1_demo_invoice_1")
        cls.amount = cls.invoice.amount_total
        cls.enable_reconcile_after_done_patcher = False

    def test_transaction(self):
        tx = self._create_transaction(
            "redirect",
            invoice_ids=[(6, 0, self.invoice.ids)],
            reference="424242",
        )
        self.assertFalse(tx.provider_id._should_build_inline_form())
        redirect_url = "https://hello.world"
        with patch.object(requests, "post") as requests_post:
            requests_post.return_value = Mock(
                json=Mock(return_value={"Data": {"RedirectURL": redirect_url}})
            )
            vals = tx._get_specific_rendering_values({})
            self.assertEqual(vals["RedirectURL"], redirect_url)
        found_tx = self.env["payment.transaction"]._get_tx_from_notification_data(
            "sumit",
            {
                "OG-ExternalIdentifier": "424242",
            },
        )
        self.assertEqual(tx, found_tx)
        found_tx = self.env["payment.transaction"]._get_tx_from_notification_data(
            "sumit", {}
        )
        self.assertFalse(found_tx)
        tx._process_notification_data({"OG-PaymentID": "42"})
        self.assertEqual(tx.provider_reference, "42")
        with patch.object(requests, "post") as requests_post:
            requests_post.return_value = Mock(
                json=Mock(return_value={"Data": {"RedirectURL": redirect_url}})
            )
            tx._finalize_post_processing()
        self.assertEqual(self.invoice.payment_state, "paid")
