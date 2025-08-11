# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io
from collections import namedtuple

from werkzeug.datastructures import MultiDict

from odoo import exceptions, fields, tools
from odoo.tests import Form, TransactionCase


class TestBankaymaAccountPortal(TransactionCase):
    def test_vendor_bill(self):
        self.env.ref("bankayma_account.tier_definition_vendor_bill").active = True
        fake_upload = namedtuple("fake_upload", ["stream", "filename"])
        user = self.env.ref("bankayma_base.vendor_b2b")
        user.operating_unit_ids += self.env.ref("operating_unit.b2c_operating_unit")
        operating_unit = self.env.ref("operating_unit.b2c_operating_unit")
        company = self.env.company
        fpos = self.env["account.fiscal.position"].search(
            [("company_id", "=", company.id)], limit=1
        )
        fpos.bankayma_tax_ids = self.env["account.tax"].create(
            {
                "name": "Imposed tax",
                "type_tax_use": "purchase",
                "company_id": company.id,
            }
        )
        fpos.bankayma_deduct_tax = True
        fpos.bankayma_deduct_tax_account_id = self.env["account.account"].search(
            [
                ("account_type", "=", "asset_current"),
            ],
            limit=1,
        )
        fpos.bankayma_deduct_tax_group_id = self.env["account.tax.group"].search(
            [],
            limit=1,
        )
        user.partner_id.write(
            {
                "bankayma_vendor_tax_percentage": 42,
                "bankayma_vendor_max_amount": 424242,
                "bankayma_tax_group_ids": [
                    (
                        6,
                        0,
                        self.env.ref("bankayma_account.tax_group_social_security").ids,
                    )
                ],
            }
        )
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .sudo()
            ._portal_create_vendor_bill(
                {
                    "operating_unit_id": str(operating_unit.id),
                    "amount": "42",
                    "description": "hello world",
                    "fpos": str(fpos.id),
                },
                MultiDict(
                    [
                        (
                            "upload",
                            fake_upload(io.BytesIO(b"hello world"), "hello_world.txt"),
                        )
                    ]
                ),
            )
        )
        self.assertTrue(invoice)
        vendor_follower = invoice.message_follower_ids.filtered(
            lambda x: x.partner_id == invoice.partner_id
        )
        self.assertIn(self.env.ref("mail.mt_comment"), vendor_follower.subtype_ids)
        attachment = self.env["ir.attachment"].search(
            [
                ("res_id", "=", invoice.id),
                ("res_model", "=", invoice._name),
            ]
        )
        self.assertTrue(attachment)
        self.assertEqual(invoice.operating_unit_id, operating_unit)
        taxes = invoice.invoice_line_ids.tax_ids
        self.assertEqual(len(taxes), 2)
        vendor_tax, imposed_tax = taxes
        self.assertEqual(imposed_tax, fpos.bankayma_tax_ids)
        self.assertEqual(
            vendor_tax.tax_group_id,
            fpos.bankayma_deduct_tax_group_id,
        )
        self.assertEqual(vendor_tax.amount, 42)
        self.assertEqual(vendor_tax.amount_type, "code")
        self.assertTrue(invoice.bankayma_vendor_max_amount, 424242)
        with (
            self.assertRaises(exceptions.UserError),
            tools.mute_logger("odoo.exceptions.UserError"),
        ):
            invoice.request_validation()
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.product_id = self.env["product.product"].search(
                    [
                        ("id", "!=", invoice.invoice_line_ids.product_id.id),
                    ],
                    limit=1,
                )
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
        invoice.invoice_line_ids._compute_tax_ids()
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
        invoice.invoice_date = fields.Date.context_today(invoice)
        self.assertEqual(invoice.validated_state, "0_draft")
        with (
            self.assertRaises(exceptions.ValidationError),
            tools.mute_logger("odoo.exceptions.ValidationError"),
        ):
            invoice.action_post()
        invoice.request_validation()
        self.assertEqual(invoice.validated_state, "1_needs_validation")
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
