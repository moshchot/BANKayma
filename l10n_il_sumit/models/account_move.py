# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sumit_document_url = fields.Char("Sumit document url", readonly=True)
    sumit_document_number = fields.Char("Sumit document number", readonly=True)

    def _to_sumit_vals(self):
        """Return a dict describing this invoice for sumit"""
        self.ensure_one()
        return {
            "Details": {
                "IsDraft": False,
                "Date": self.date.isoformat(),
                "Customer": self.partner_id._to_sumit_vals(),
                "SendByEmail": {
                    "EmailAddress": self.partner_id.email or None,
                    "Original": True,
                    "SendAsPaymentRequest": False,
                },
                "Language": self.env["sumit.account"].sumit_language(
                    self.partner_id.lang
                ),
                "Currency": self.env["sumit.account"].sumit_currency(self.currency_id),
                "Type": self.journal_id["sumit_type_" + self.move_type]
                or self.journal_id.sumit_type,
                "Description": self.name,
                "ExternalReference": self.name,
                "OpeningTextHTML": None,
                "OpeningText": None,
                "ClosingTextHTML": None,
                "ClosingText": None,
                "DueDate": self.invoice_date_due.isoformat()
                if self.invoice_date_due
                else None,
            },
            "Items": [line._to_sumit_vals() for line in self.invoice_line_ids],
            "Payments": [
                payment._to_sumit_vals()
                for payment in self.line_ids.mapped(
                    "full_reconcile_id.reconciled_line_ids.move_id.payment_ids"
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
        """
        Create sumit document if journal is configured for it, but only if
        the payment isn't done via sumit anyways
        """
        payments = self.line_ids.mapped(
            "full_reconcile_id.reconciled_line_ids.move_id.payment_ids"
        )
        if self._invoice_paid_hook_use_sumit():
            result = self.env["sumit.account"]._request(
                "/accounting/documents/create",
                self._to_sumit_vals(),
            )
            payments.write(
                {
                    "memo": result.get("DocumentNumber"),
                    "sumit_document_url": result.get("DocumentDownloadURL"),
                }
            )
            self.message_post(
                body=_(
                    "Sumit document: "
                    '<a href="%(DocumentDownloadURL)s">%(DocumentNumber)s</a>'
                )
                % result
            )

        return super()._invoice_paid_hook()

    def _invoice_paid_hook_use_sumit(self):
        payments = self.line_ids.mapped(
            "full_reconcile_id.reconciled_line_ids.move_id.payment_ids"
        )
        payment_provider = payments.payment_transaction_id.provider_id
        return self and self.journal_id.use_sumit and payment_provider.code != "sumit"
