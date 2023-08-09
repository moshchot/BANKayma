# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sumit_document_url = fields.Char("Sumit document", readonly=True)

    def _to_sumit_vals(self):
        """Return a dict describing this invoice for sumit"""
        return {
            "Details": {
                "IsDraft": False,
                "Date": self.date.isoformat(),
                "Customer": {
                    "ExternalIdentifier": None,
                    "NoVAT": None,
                    "SearchMode": 0,
                    "Name": self.partner_id.name,
                    "Phone": self.partner_id.phone or None,
                    "EmailAddress": self.partner_id.email or None,
                    "City": self.partner_id.city or None,
                    "Address": self.partner_id.street or None,
                    "ZipCode": self.partner_id.zip or None,
                    "CompanyNumber": None,
                    "ID": None,
                    "Folder": None,
                },
                "SendByEmail": {
                    "EmailAddress": self.partner_id.email or None,
                    "Original": True,
                    "SendAsPaymentRequest": False,
                },
                "Language": self.env["sumit.account"].sumit_language(
                    self.partner_id.lang
                ),
                "Currency": self.env["sumit.account"].sumit_currency(self.currency_id),
                "Type": "1",
                "Description": self.name,
                "ExternalReference": None,
                "OpeningTextHTML": None,
                "OpeningText": None,
                "ClosingTextHTML": None,
                "ClosingText": None,
                "DueDate": None,
            },
            "Items": [
                {
                    "Quantity": line.quantity,
                    "UnitPrice": line.price_unit,
                    "TotalPrice": line.price_subtotal,
                    "DocumentCurrency_UnitPrice": None,
                    "DocumentCurrency_TotalPrice": None,
                    "Description": line.name or None,
                    "Item": {
                        "ID": None,
                        "Name": line.product_id.name or None,
                        "Description": None,
                        "Price": line.product_id.list_price,
                        "Currency": self.env["sumit.account"].sumit_currency(
                            self.env.company.currency_id
                        ),
                        "Cost": line.product_id.standard_price,
                        "ExternalIdentifier": None,
                        "SKU": line.product_id.default_code or None,
                        "SearchMode": 0,
                    },
                }
                for line in self.invoice_line_ids
            ],
            "Payments": [
                {
                    "Amount": payment.amount,
                    "DocumentCurrency_Amount": None,
                    "Type": None,
                    "Details_General": None,
                    "Details_Cash": None,
                    "Details_BankTransfer": None,
                    "Details_Cheque": None,
                    "Details_CreditCard": {
                        "CardBrand": None,
                        "Last4Digits": None,
                        "FirstPayment": None,
                        "EachPayment": None,
                        "Payments": None,
                    },
                    "Details_Other": None,
                    "Details_Digital": None,
                    "Details_TaxWithholding": None,
                }
                for payment in self.line_ids.mapped(
                    "full_reconcile_id.reconciled_line_ids.move_id.payment_id"
                )
            ],
            "VATIncluded": False,
            "VATRate": None,
            "OriginalDocumentID": None,
            "ResponseLanguage": self.env["sumit.account"].sumit_language(
                self.env.user.lang
            ),
        }

    def _invoice_paid_hook(self):
        if self.journal_id.use_sumit:
            result = self.env["sumit.account"]._request(
                "/accounting/documents/create",
                self._to_sumit_vals(),
            )
            self.line_ids.mapped(
                "full_reconcile_id.reconciled_line_ids.move_id.payment_id"
            ).write(
                {
                    "ref": result.get("DocumentNumber"),
                    "sumit_document_url": result.get("DocumentDownloadURL"),
                }
            )

        return super()._invoice_paid_hook()
