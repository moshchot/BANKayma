# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io
from collections import namedtuple

from werkzeug.datastructures import MultiDict

from odoo.tests.common import TransactionCase


class TestBankaymaAccountPortal(TransactionCase):
    def test_vendor_bill(self):
        fake_upload = namedtuple("fake_upload", ["stream", "filename"])
        user = self.env.ref("bankayma_base.vendor_child_comp1")
        fpos = self.env["account.fiscal.position"].search([], limit=1)
        fpos.bankayma_tax_id = self.env["account.tax"].search(
            [("type_tax_use", "=", "purchase")], limit=1
        )
        invoice = (
            self.env["account.move"]
            .with_user(user)
            .sudo()
            ._portal_create_vendor_bill(
                {
                    "company": self.env.company,
                    "amount": "42",
                    "description": "hello world",
                    "fpos": fpos.id,
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
        self.assertTrue(invoice.invoice_line_ids.tax_ids)
        self.assertEqual(invoice.invoice_line_ids.tax_ids, fpos.bankayma_tax_id)
