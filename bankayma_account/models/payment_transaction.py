# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    is_recurrent = fields.Boolean()
    bankayma_tax_number = fields.Char()

    def _process_notification_data(self, notification_data):
        """Coerce current company to provider's company for further processing"""
        for this in self.filtered(lambda x: x.is_donation and not x.invoice_ids):
            partner = this.partner_id
            if (
                self.env.user._is_public()
                and self.env.user.partner_id == this.partner_id
            ):
                partner = self.env["res.partner"].create(
                    {
                        "name": this.partner_name,
                        "email": this.partner_email,
                    }
                )
            donation_product = (
                this.company_id.donation_credit_transfer_product_id.with_company(
                    this.company_id
                )
            )
            donation_account = donation_product.property_account_income_id
            this.invoice_ids = (
                self.env["account.move"]
                .sudo()
                .with_company(this.company_id)
                .create(
                    {
                        "move_type": "out_invoice",
                        "partner_id": partner.id,
                        "invoice_line_ids": [
                            fields.Command.create(
                                {
                                    "product_id": donation_product.id,
                                    "account_id": donation_account.id,
                                    "name": this._to_sumit_vals_name(this.is_recurrent),
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

            if not (self.sumit_details or {}).get("Payments"):
                payment_details = self.provider_id.sumit_account_id._request(
                    "/billing/payments/get",
                    {
                        "PaymentID": notification_data["OG-PaymentID"],
                    },
                )
                payment_method_dict = {}
                if notification_data.get("OG-PaymentType") == "CreditCard":
                    installments = 1
                    if payment_details["Payment"]["NonFirstPaymentAmount"]:
                        installments = 1 + int(
                            (
                                payment_details["Payment"]["Amount"]
                                - payment_details["Payment"]["FirstPaymentAmount"]
                            )
                            / payment_details["Payment"]["NonFirstPaymentAmount"]
                        )
                    payment_method_dict["Details_CreditCard"] = {
                        "Last4Digits": payment_details["Payment"]["PaymentMethod"][
                            "CreditCard_LastDigits"
                        ],
                        "FirstPayment": payment_details["Payment"][
                            "FirstPaymentAmount"
                        ],
                        "EachPayment": payment_details["Payment"][
                            "NonFirstPaymentAmount"
                        ],
                        "Payments": installments,
                    }

                self.sumit_details = dict(
                    self.sumit_details or {},
                    Payments=[
                        dict(
                            payment_method_dict,
                            Amount=payment_details["Payment"]["Amount"],
                        ),
                    ],
                )

            donation_product = (
                self.company_id.donation_credit_transfer_product_id.with_company(
                    self.company_id
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
                partner = self.invoice_ids.partner_id[:1] or self.partner_id
                contract = (
                    self.env["contract.contract"]
                    .with_company(self.company_id)
                    .create(
                        {
                            "name": payload["Items"][0]["Item"]["Name"],
                            "contract_type": "sale",
                            "partner_id": partner.id,
                            "invoice_partner_id": partner.id,
                            "date_start": date.today(),
                            "recurring_next_date": date.today()
                            + relativedelta(months=1),
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
                                        "name": self._to_sumit_vals_name(
                                            self.is_recurrent
                                        ),
                                    }
                                ),
                            ],
                        }
                    )
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
        if self.bankayma_tax_number:
            result["Customer"]["CompanyNumber"] = self.bankayma_tax_number
        return result

    def _to_sumit_vals_name(self, recurrent):
        donation_product = (
            self.company_id.donation_credit_transfer_product_id.with_company(
                self.company_id
            )
        )
        return (
            recurrent
            and _("[%(account_code)s] recurrent donation to %(company_name)s")
            or _("[%(account_code)s] donation to %(company_name)s")
        ) % {
            "account_code": donation_product.property_account_income_id.code,
            "company_name": self.company_id.name,
        }
