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
            },
        )
        cls.invoice = cls.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("payment_state", "=", "not_paid"),
            ],
            limit=1,
        )

    def test_transaction(self):
        tx = self._create_transaction(
            "redirect", invoice_ids=[(6, 0, self.invoice.ids)]
        )
        self.assertFalse(tx.provider_id._should_build_inline_form())
        redirect_url = "https://hello.world"
        with patch.object(requests, "post") as requests_post:
            requests_post.return_value = Mock(
                json=Mock(return_value={"Data": {"RedirectURL": redirect_url}})
            )
            vals = tx._get_specific_rendering_values({})
            self.assertEqual(vals["RedirectURL"], redirect_url)
