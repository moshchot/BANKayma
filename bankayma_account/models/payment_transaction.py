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
        for this in self.filtered(lambda x: x.is_donation and not x.invoice_ids):
            donation_product = (
                this.company_id.donation_credit_transfer_product_id.with_company(
                    this.company_id
                )
            )
            donation_account = donation_product.property_account_income_id
            this.invoice_ids = (
                self.env["account.move"]
                .sudo()
                .create(
                    {
                        "move_type": "out_invoice",
                        "partner_id": this.partner_id.id,
                        "invoice_line_ids": [
                            fields.Command.create(
                                {
                                    "product_id": donation_product.id,
                                    "account_id": donation_account.id,
                                    "name": this._to_sumit_vals_name(True),
                                    "price_unit": this.amount,
                                    "tax_ids": [fields.Command.set([])],
                                }
                            ),
                        ],
                        "journal_id": this.company_id.donation_journal_id.id,
                    }
                )
            )
        result = super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._process_notification_data(notification_data)
        if self.provider_code == "sumit" and notification_data.get("OG-PaymentID"):
            donation_product = (
                self.company_id.donation_credit_transfer_product_id.with_company(
                    this.company_id
                )
            )
            if self.is_donation and self.is_recurrent:
                payload = {
                    "Customer": {
                        "ID": notification_data["OG-CustomerID"],
                    },
                    "PaymentMethod": None,
                    "Items": [
                        {
                            "Item": {
                                "Name": self._to_sumit_vals_name(True),
                                "Duration_Months": 1,
                            },
                            "UnitPrice": self.amount,
                            "Date_Start": (
                                date.today() + relativedelta(months=1)
                            ).isoformat(),
                            "Duration_Days": 0,
                            "Duration_Months": 1,
                            "Recurrence": 12,
                        }
                    ],
                }
                result = self.provider_id.sumit_account_id._request(
                    "/billing/recurring/charge",
                    payload,
                )
                contract = self.env["contract.contract"].create(
                    {
                        "name": payload["Items"][0]["Item"]["Name"],
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
                        "journal_id": self.company_id.donation_journal_id.id,
                        "contract_line_fixed_ids": [
                            fields.Command.create(
                                {
                                    "product_id": donation_product.id,
                                    "price_unit": self.amount,
                                    "name": self._to_sumit_vals_name(self.is_recurrent),
                                }
                            ),
                        ],
                    }
                )
                self.invoice_ids.invoice_line_ids.write(
                    {
                        "contract_line_id": contract.contract_line_fixed_ids.id,
                    }
                )
        return result

    def _finalize_post_processing(self):
        """Coerce current company to provider's company for further processing"""
        return super(
            PaymentTransaction, self.with_company(self.provider_id.company_id)
        )._finalize_post_processing()

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        if self.is_donation and len(result.get("Items", [])) == 1:
            result["Items"][0]["Item"]["Name"] = self._to_sumit_vals_name(
                self.is_recurrent
            )
            result["DocumentDescription"] = result["Items"][0]["Item"]["Name"]
            result["Items"][0]["Item"]["Description"] = None
            result["Items"][0]["Description"] = None
        return result

    def _to_sumit_vals_name(self, recurrent):
        donation_product = self.company_id.donation_credit_transfer_product_id
        return (
            recurrent
            and "[%(account_code)s] recurrent donation to %(company_name)s"
            or "[%(account_code)s] donation to %(company_name)s"
        ) % {
            "account_code": donation_product.property_account_income_id.code,
            "company_name": self.company_id.name,
        }
