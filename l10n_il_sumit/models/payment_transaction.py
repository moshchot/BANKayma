# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import urlparse, urlunparse

from odoo import _, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        if self.provider_id.code == "sumit":
            payload = self._to_sumit_vals()
            result = self.provider_id.sumit_account_id._request(
                "/billing/payments/beginredirect", payload
            )
            return result
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
                # TODO: use partner_id._to_sumit_vals() if not partner_id.is_public?
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
                self.is_donation and "4" or "0",
            ),
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
            "MaximumPayments": None,
            "SendUpdateByEmailAddress": True,
            "ExpirationHours": None,
            "Theme": None,
            "Language": invoice_sumit_vals.get("Details", {}).get("Language")
            or self.env["sumit.account"].sumit_language(self.env.lang),
            "Header": None,
            "UpdateOrganizationOnSuccess": None,
            "UpdateOrganizationOnFailure": None,
            "UpdateCustomerOnSuccess": None,
            "DocumentDescription": None,
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
            if "OG-DocumentNumber" in notification_data:
                details = self.provider_id.sumit_account_id._request(
                    "/accounting/documents/getdetails",
                    {
                        "DocumentType": self._to_sumit_vals()["DocumentType"],
                        "DocumentNumber": notification_data["OG-DocumentNumber"],
                    },
                )
                self.invoice_ids.message_post(
                    body=_(
                        'Sumit document: <a href="%(DocumentDownloadURL)s">'
                        "%(DocumentNumber)s</a>"
                    )
                    % details
                )
        return result
