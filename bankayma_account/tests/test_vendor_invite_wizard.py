# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import parse_qs, urlparse

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestVendorInviteWizard(TransactionCase):
    def test_vendor_invite_flow(self):
        self.env.ref("bankayma_account.template_vendor_invite").auto_delete = False
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
        all_mails = self.env["mail.mail"].search([])
        wizard.action_send_mail()
        new_mail = self.env["mail.mail"].search([]) - all_mails
        self.assertTrue(new_mail)
        login_links = etree.fromstring(f"<t>{new_mail.body}</t>").xpath(
            '//a[contains(@href, "token")]'
        )
        self.assertEqual(len(login_links), 1)
        query = parse_qs(urlparse(login_links[0].attrib["href"]).query)
        token = "".join(query["token"])
        _dummy, _dummy = self.env["res.users"].signup(
            {
                "login": vendor.email,
                "name": vendor.name,
                "password": "password",
            },
            token,
        )
        self.assertTrue(vendor.user_ids)
        self.assertEqual(
            "".join(query["redirect"]),
            "/my/account?redirect=/my/invoices/new",
        )
        self.assertIn(
            self.env.ref("bankayma_base.group_vendor"),
            vendor.user_ids.groups_id,
        )
