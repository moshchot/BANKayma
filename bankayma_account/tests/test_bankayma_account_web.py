# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase
from odoo.tools.misc import mute_logger


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

    def test_profile(self):
        self.authenticate("vendor_child_comp1", "vendor_child_comp1")
        self.url_open("/my")
        self.url_open("/my/account")
        self.url_open("/my/invoices/new")
        # TODO: actually do something useful here, run a tour or similar
