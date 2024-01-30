# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestVendorInviteWizard(TransactionCase):
    def test_vendor_invite_flow(self):
        vendor = self.env.ref("base.res_partner_address_15")
        self.assertFalse(vendor.user_ids)
        wizard_action = vendor.action_invite_vendor()
        wizard = (
            self.env[wizard_action["res_model"]]
            .with_context(
                active_model=vendor._name,
                active_id=vendor.id,
                active_ids=vendor.ids,
                **safe_eval(wizard_action["context"]),
            )
            .create({})
        )
        wizard.action_send_mail()
        login, password = self.env["res.users"].signup(
            {
                "login": vendor.email,
                "password": "hello world",
            },
            token=vendor.signup_token,
        )
        self.assertTrue(vendor.user_ids)
        self.assertEqual(
            vendor.user_ids.login_redirect,
            "/my/account?redirect=/my/invoices/new",
        )
