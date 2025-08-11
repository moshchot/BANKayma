# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    is_recurrent = fields.Boolean()
    bankayma_tax_number = fields.Char()
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)

    def _process_notification_data(self, notification_data):
        """
        Create invoice for donations
        """
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
                this.company_id.donation_credit_transfer_product_id.with_ou(
                    this.operating_unit_id
                )
            )
            donation_account = donation_product.property_account_income_id
            this.invoice_ids = (
                self.env["account.move"]
                .sudo()
                .with_ou(this.operating_unit_id)
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
        return super()._process_notification_data(notification_data)

    def _post_process(self):
        super()._post_process()

        if not (self.sumit_details or {}).get("OG-PaymentID"):
            return

        if not (self.sumit_details or {}).get("Payments"):
            payment_details = self.provider_id.sumit_account_id._request(
                "/billing/payments/get",
                {
                    "PaymentID": self.sumit_details["OG-PaymentID"],
                },
            )
            payment_method_dict = {}
            if self.sumit_details.get("OG-PaymentType") == "CreditCard":
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
                    "FirstPayment": payment_details["Payment"]["FirstPaymentAmount"],
                    "EachPayment": payment_details["Payment"]["NonFirstPaymentAmount"],
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

        for line in self.invoice_ids.invoice_line_ids.filtered(
            lambda x, self=self: x.product_id.sumit_recurrence
            or (self.is_donation and self.is_recurrent)
        ):
            product = line.product_id
            if self.is_donation and self.is_recurrent:
                recurrence_days = 0
                recurrence_months = 1
            else:
                recurrence_days = (
                    product.sumit_recurrence_interval
                    if product.sumit_recurrence == "daily"
                    else 0
                )
                recurrence_months = (
                    product.sumit_recurrence_interval
                    if product.sumit_recurrence == "monthly"
                    else 0
                )
            if not recurrence_months and not recurrence_days:
                continue
            payload = {
                "Customer": {
                    "ID": self.sumit_details["OG-CustomerID"],
                },
                "PaymentMethod": None,
                "Items": [
                    {
                        "Item": {
                            "Name": line.name,
                            "Duration_Days": recurrence_days,
                            "Duration_Months": recurrence_months,
                        },
                        "UnitPrice": line.price_total,
                        "Date_Start": (
                            date.today()
                            + relativedelta(
                                months=recurrence_months, days=recurrence_days
                            )
                        ).isoformat(),
                        "Duration_Days": recurrence_days,
                        "Duration_Months": recurrence_months,
                        "Recurrence": 0,
                    }
                ],
                "UpdateCustomerByEmail": True,
                "SendCopyToOrganization": True,
            }
            result = self.provider_id.sumit_account_id._request(
                "/billing/recurring/charge",
                payload,
            )
            partner = line.move_id.partner_id or self.partner_id
            contract = (
                self.env["contract.contract"]
                .with_ou(line.operating_unit_id)
                .create(
                    {
                        "name": line.name,
                        "contract_type": "sale",
                        "partner_id": partner.id,
                        "invoice_partner_id": partner.id,
                        "date_start": date.today(),
                        "recurring_next_date": date.today()
                        + relativedelta(months=recurrence_months, days=recurrence_days),
                        "recurring_rule_type": "monthly"
                        if recurrence_months
                        else "daily",
                        "recurring_invoicing_type": "pre-paid",
                        "recurring_interval": recurrence_months or recurrence_days,
                        "code": (result.get("Payment", {}) or {}).get("ID")
                        or result.get("DocumentID")
                        or ", ".join(
                            map(str, result.get("RecurringCustomerItemIDs", []))
                        ),
                        "journal_id": line.move_id.journal_id.id,
                        "contract_line_fixed_ids": [
                            fields.Command.create(
                                {
                                    "product_id": product.id,
                                    "price_unit": self.amount,
                                    "name": line.name,
                                }
                            ),
                        ],
                        "sumit_details": result,
                    }
                )
            )
            line.write(
                {
                    "contract_line_id": contract.contract_line_fixed_ids.id,
                }
            )

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
        donation_product = self.company_id.donation_credit_transfer_product_id
        return (
            recurrent
            and _("[%(account_code)s] recurrent donation to %(company_name)s")
            or _("[%(account_code)s] donation to %(company_name)s")
        ) % {
            "account_code": donation_product.property_account_income_id.code,
            "company_name": self.company_id.name,
        }
