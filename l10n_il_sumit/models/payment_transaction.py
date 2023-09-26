# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import urlparse, urlunparse

from odoo import models


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
        invoice_sumit_vals = self.invoice_ids._to_sumit_vals()
        base_url = urlparse(self.provider_id.get_base_url())
        return {
            "Customer": invoice_sumit_vals.get("Details", {}).get("Customer", {}),
            "Items": [
                {
                    "Quantity": 1,
                    "Total": item["TotalPrice"],
                    "UnitPrice": item["TotalPrice"],
                    "Item": item["Item"],
                    "Description": item["Description"],
                }
                for item in invoice_sumit_vals.get("Items", [])
            ],
            "VATIncluded": invoice_sumit_vals.get("VATIncluded", False),
            "DocumentType": invoice_sumit_vals.get("Details", {}).get("Type", None),
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
            "SendUpdateByEmailAddress": False,
            "ExpirationHours": None,
            "Theme": None,
            "Language": invoice_sumit_vals.get("Details", {}).get("Language", None),
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
        return result
