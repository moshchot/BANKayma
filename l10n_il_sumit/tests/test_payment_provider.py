# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


import requests_mock

from odoo.tests import tagged

from odoo.addons.payment.tests.common import PaymentCommon


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

    @requests_mock.Mocker()
    def test_transaction(self, requests_mock):
        redirect_url = "https://hello.world"
        requests_mock.post(
            "/billing/payments/beginredirect",
            json={"Data": {"RedirectURL": redirect_url}},
        )
        requests_mock.post(
            "/billing/payments/get",
            json={"Data": {"Payment": {"Amount": self.invoice.amount_total}}},
        )
        requests_mock.post(
            "/accounting/documents/getdetails",
            json={
                "Data": {
                    "Payments": [{"Amount": self.invoice.amount_total}],
                    "DocumentDownloadURL": "https://test.com",
                    "DocumentNumber": "424242",
                }
            },
        )
        tx = self._create_transaction(
            "redirect",
            invoice_ids=[(6, 0, self.invoice.ids)],
            reference="424242",
        )
        self.assertFalse(tx.provider_id._should_build_inline_form())
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
        tx._process_notification_data(
            {"OG-PaymentID": "42", "OG-DocumentNumber": "424242"}
        )
        self.assertEqual(tx.provider_reference, "42")
        tx._finalize_post_processing()
        self.assertEqual(self.invoice.payment_state, "paid")
