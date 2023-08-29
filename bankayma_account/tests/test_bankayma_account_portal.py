# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io
from collections import namedtuple

from werkzeug.datastructures import MultiDict

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestBankaymaAccountPortal(TransactionCase):
    def test_vendor_bill(self):
        fake_upload = namedtuple("fake_upload", ["stream", "filename"])
        user = self.env.ref("bankayma_base.vendor_child_comp1")
        user.company_ids += self.env.ref("l10n_il.demo_company_il")
        company = self.env.ref("l10n_il.demo_company_il")
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
                ("company_id", "=", company.id),
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
                "purchase_tax_ids": [(6, 0, fpos.bankayma_tax_ids.ids)],
            }
        )
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .sudo()
            ._portal_create_vendor_bill(
                {
                    "company": company,
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
        attachment = self.env["ir.attachment"].search(
            [
                ("res_id", "=", invoice.id),
                ("res_model", "=", invoice._name),
            ]
        )
        self.assertTrue(attachment)
        self.assertEqual(invoice.company_id, company)
        taxes = invoice.invoice_line_ids.tax_ids
        self.assertEqual(len(taxes), 2)
        vendor_tax, imposed_tax = taxes
        self.assertEqual(imposed_tax, fpos.bankayma_tax_ids)
        self.assertEqual(
            vendor_tax.tax_group_id,
            fpos.bankayma_deduct_tax_group_id,
        )
        self.assertEqual(vendor_tax.amount, 42)
        self.assertTrue(invoice.bankayma_vendor_max_amount, 424242)
        self.assertTrue(invoice.invoice_line_ids.bankayma_immutable)
        with Form(invoice) as invoice_form:
            invoice_form.invoice_line_ids.product_id = self.env[
                "product.product"
            ].search(
                [
                    ("id", "!=", invoice.invoice_line_ids.product_id.id),
                ]
            )
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
        invoice.invoice_line_ids._compute_tax_ids()
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
        invoice.invoice_line_ids.bankayma_immutable = False
        invoice.invoice_line_ids._compute_tax_ids()
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
        invoice.invoice_date = fields.Date.context_today(invoice)
        invoice.action_post()
        self.assertEqual(taxes, invoice.invoice_line_ids.tax_ids)
