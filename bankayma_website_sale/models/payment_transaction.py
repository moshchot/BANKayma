# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from math import copysign

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _to_sumit_vals(self):
        """Set sumit document type to 8 (order) for orders"""
        result = super()._to_sumit_vals()
        if not self.invoice_ids and self.sale_order_ids.website_id:
            result["DocumentType"] = "8"
        return result

    def _create_payment(self, **extra_create_values):
        """Split transaction according to companies in invoices, if any"""
        self.ensure_one()

        if (
            not self.invoice_ids.company_id
            or self.invoice_ids.company_id == self.company_id
        ):
            return super()._create_payment(**extra_create_values)

        amount = abs(self.amount)
        payments = self.env["account.payment"]

        for company in self.invoice_ids.company_id:
            company_invoices = self.invoice_ids.filtered(
                lambda x: x.company_id == company and x.payment_state != "paid"
            )
            if not company_invoices:
                continue
            company_amount = sum(company_invoices.mapped("amount_total"))
            company_transaction = self.new(
                {
                    "provider_id": self.provider_id._company_cascade_get_all(company),
                    "provider_code": self.provider_id._company_cascade_get_all(
                        company
                    ).code,
                    "company_id": company,
                    "reference": self.reference,
                    "provider_reference": self.provider_reference,
                    "amount": copysign(company_amount, self.amount),
                    "currency_id": company_invoices.currency_id,
                    "state": self.state,
                }
            ).with_company(company)
            # new() wraps existing recordsets into newid objects, we can't have that here
            # (fails in reconcile() because it wants to write the id of invoice lines)
            company_transaction._cache["invoice_ids"] = tuple(company_invoices.ids)
            payments += super(PaymentTransaction, company_transaction)._create_payment(
                **extra_create_values
            )
            amount -= company_invoices.currency_id._convert(
                company_amount, self.currency_id, company, self.create_date
            )

        return payments
