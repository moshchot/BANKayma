# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    is_recurrent = fields.Boolean()

    def _process_notification_data(self, notification_data):
        """Coerce current company to provider's company for further processing"""
        result = super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._process_notification_data(notification_data)
        if self.provider_code == "sumit" and notification_data.get("OG-PaymentID"):
            if self.is_recurrent:
                result = self.provider_id.sumit_account_id._request(
                    "/billing/recurring/charge",
                    {
                        "Customer": {
                            "ID": notification_data["OG-CustomerID"],
                        },
                        "PaymentMethod": None,
                        "Items": [
                            {
                                "Item": {
                                    "Name": self.display_name,
                                    "Duration_Months": 1,
                                },
                                "UnitPrice": self.amount,
                                "Date_Start": (
                                    date.today() + relativedelta(months=1)
                                ).isoformat(),
                                "Duration_Days": 0,
                                "Duration_Months": 1,
                                "Recurrence": 0,
                            }
                        ],
                    },
                )
                self.env["contract.contract"].create(
                    {
                        "name": self.display_name,
                        "contract_type": "sale",
                        "partner_id": self.env.user.partner_id.id,
                        "invoice_partner_id": self.env.user.partner_id.id,
                        "date_start": date.today(),
                        "recurring_next_date": date.today() + relativedelta(months=1),
                        "recurring_rule_type": "monthly",
                        "recurring_invoicing_type": "pre-paid",
                        "recurring_interval": 1,
                        "code": result.get("Data", {}).get("Payment", {}).get("ID")
                        or result.get("Data", {}).get("DocumentID"),
                    }
                )
        return result

    def _finalize_post_processing(self):
        """Coerce current company to provider's company for further processing"""
        return super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._finalize_post_processing()

    def _create_payment(self, **extra_create_values):
        payment_method_line = None
        if self.is_donation and self.company_id.donation_account_id:
            # poison the cache to have super create move line with configured account
            payment_method_line = (
                self.provider_id.journal_id.inbound_payment_method_line_ids.filtered(
                    lambda x, self=self: x.code == self.provider_id.code
                )
            )
            payment_method_line._cache[
                "payment_account_id"
            ] = self.company_id.donation_account_id.id
            # pass donation product as default
            self = self.with_context(
                default_product_id=self.company_id.donation_credit_transfer_product_id.id
            )
        result = super(PaymentTransaction, self)._create_payment(**extra_create_values)
        if payment_method_line:
            payment_method_line.invalidate_recordset(["payment_account_id"])
        return result

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        if self.is_donation and len(result.get("Items", [])) == 1:
            result["Items"][0]["Item"]["Name"] = (
                self.company_id.donation_credit_transfer_product_id.display_name
                or self.company_id.donation_account_id.name
                or result["Items"][0]["Item"]["Name"]
            )
        return result
