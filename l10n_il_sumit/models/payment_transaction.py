# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import parse_qs, urlparse, urlunparse

from odoo import _, fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    sumit_document_url = fields.Char("Sumit document", readonly=True)
    sumit_details = fields.Json()

    def _get_specific_rendering_values(self, processing_values):
        if self.provider_id.code == "sumit":
            payload = self._to_sumit_vals()
            sumit_result = self.provider_id.sumit_account_id._request(
                "/billing/payments/beginredirect", payload
            )
            sumit_url = urlparse(sumit_result["RedirectURL"])
            return {
                "redirect": urlunparse(sumit_url[:3] + ("", "", "")),
                "values": {
                    key: "".join(value)
                    for key, value in parse_qs(sumit_url.query).items()
                },
            }
        return super()._get_specific_rendering_values(processing_values)

    def _to_sumit_vals(self):
        invoice_sumit_vals = (
            self.invoice_ids and self.invoice_ids._to_sumit_vals() or {}
        )
        base_url = urlparse(self.provider_id.get_base_url())
        return {
            "Customer": invoice_sumit_vals.get("Details", {}).get("Customer", {})
            if invoice_sumit_vals
            else {
                "ExternalIdentifier": None,
                "NoVAT": None,
                "SearchMode": 0,
                "Name": self.partner_name,
                "Phone": self.partner_phone or None,
                "EmailAddress": self.partner_email or None,
                "City": self.partner_city or None,
                "Address": self.partner_address or None,
                "ZipCode": self.partner_zip or None,
                "CompanyNumber": None,
                "ID": None,
                "Folder": None,
            },
            "Items": [
                {
                    "Quantity": 1,
                    "Total": item["TotalPrice"],
                    "UnitPrice": item["TotalPrice"],
                    "Item": item["Item"],
                    "Description": item["Description"],
                }
                for item in invoice_sumit_vals.get(
                    "Items",
                    [
                        {
                            "TotalPrice": self.amount,
                            "Item": {
                                "ID": None,
                                "Name": self.display_name or None,
                                "Description": None,
                                "Price": self.amount,
                                "Currency": None,
                                "Cost": None,
                                "ExternalIdentifier": None,
                                "SKU": None,
                                "SearchMode": 0,
                            },
                            "Description": self.display_name,
                        }
                    ],
                )
            ],
            "VATIncluded": invoice_sumit_vals.get("VATIncluded", False),
            "DocumentType": invoice_sumit_vals.get("Details", {}).get(
                "Type",
                ("is_donation" in self._fields and self.is_donation) and "4" or "0",
            ),
            "DocumentDescription": invoice_sumit_vals.get("Details", {}).get(
                "Description",
            )
            or self.reference,
            "RedirectURL": urlunparse(
                (
                    base_url.scheme,
                    base_url.netloc,
                    "payment/sumit/return",
                    None,
                    None,
                    None,
                )
            ),
            "ExternalIdentifier": self.reference,
            "MaximumPayments": self.provider_id.sumit_installment_count
            if self.amount >= self.provider_id.sumit_installment_threshold
            else None,
            "SendUpdateByEmailAddress": invoice_sumit_vals.get("Details", {})
            .get("Customer", {})
            .get("EmailAddress")
            or self.partner_email
            or None,
            "ExpirationHours": None,
            "Theme": None,
            "Language": invoice_sumit_vals.get("Details", {}).get("Language")
            or self.env["sumit.account"].sumit_language(self.env.lang),
            "Header": None,
            "UpdateOrganizationOnSuccess": None,
            "UpdateOrganizationOnFailure": None,
            "UpdateCustomerOnSuccess": None,
            "DraftDocument": None,
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        result = super()._get_tx_from_notification_data(
            provider_code, notification_data
        )
        if not result and provider_code == "sumit":
            result = self.search(
                [
                    ("provider_code", "=", "sumit"),
                    ("reference", "=", notification_data.get("OG-ExternalIdentifier")),
                ]
            )
        return result

    def _process_notification_data(self, notification_data):
        result = super()._process_notification_data(notification_data)
        if self.provider_code == "sumit" and notification_data.get("OG-PaymentID"):
            self.provider_reference = notification_data["OG-PaymentID"]
            self._set_done()
            self.sumit_details = notification_data
            if "OG-DocumentNumber" in notification_data:
                details = self.provider_id.sumit_account_id._request(
                    "/accounting/documents/getdetails",
                    {
                        "DocumentType": self._to_sumit_vals()["DocumentType"],
                        "DocumentNumber": notification_data["OG-DocumentNumber"],
                    },
                )
                self.sumit_details = dict(self.sumit_details or {}, **details)
                if self.invoice_ids:
                    self.invoice_ids.message_post(
                        body=_(
                            'Sumit document: <a href="%(DocumentDownloadURL)s">'
                            "%(DocumentNumber)s</a>"
                        )
                        % details
                    )

                self.sumit_document_url = details["DocumentDownloadURL"]

        if self.provider_code == "sumit" and notification_data.get("OG-CustomerID"):
            self.invoice_ids.partner_id.filtered(lambda x: not x.sumit_id).write(
                {"sumit_id": notification_data["OG-CustomerID"]}
            )

        return result

    def _create_payment(self, **extra_create_values):
        payment = super()._create_payment(**extra_create_values)

        payment.sumit_document_url = self.sumit_document_url

        return payment
