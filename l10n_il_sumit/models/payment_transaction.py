# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
            "RedirectURL": "https://test.com",
            "ExternalIdentifier": None,
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
