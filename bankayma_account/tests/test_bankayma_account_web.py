# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged
from odoo.tools.misc import mute_logger


@tagged("-at_install", "post_install")
class TestBankaymaAccountWeb(HttpCase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.http")
    def test_mail_redirect(self):
        move = (
            self.env["account.move"]
            .with_user(self.env.ref("base.user_demo"))
            .search([], limit=1)
        )
        response = self.url_open("/mail/view?model=account.move&res_id=%d" % move.id)
        self.assertIn("/web/login", response.url)
        self.authenticate("demo", "demo")
        response = self.url_open(
            "/mail/view?model=account.move&res_id=%d" % move.id, allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn("action", response.headers.get("location", ""))

    def test_vendor_portal_tour(self):
        vendor_invoice_domain = [
            ("partner_id", "=", self.env.ref("bankayma_base.vendor_b2b").partner_id.id)
        ]
        AccountMove = self.env["account.move"]
        self.assertFalse(AccountMove.search(vendor_invoice_domain))
        self.start_tour("/my", "bankayma_account_vendor_portal", login="vendor_b2b")
        vendor_invoice = AccountMove.search(vendor_invoice_domain)
        self.assertTrue(vendor_invoice)
