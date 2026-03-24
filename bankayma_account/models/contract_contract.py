import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ContractContrac(models.Model):
    _inherit = "contract.contract"

    sumit_details = fields.Json()

    def _sumit_process_invoices(self):
        """
        Search payments matching draft/posted invoices, and post/mark as paid invoices
        with payments
        """
        for invoice in self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("state", "!=", "cancel"),
                ("payment_state", "=", "not_paid"),
                ("line_ids.contract_line_id.contract_id.sumit_details", "!=", False),
            ]
        ):
            _logger.info("searching matches for %s [id %d]", invoice.name, invoice.id)
            invoice = invoice.with_company(invoice.company_id).with_context(
                bankayma_force_sumit=False
            )
            contract = invoice.line_ids.contract_line_id.contract_id
            contract_recurring_items = set(
                (contract.sumit_details or {}).get("RecurringCustomerItemIDs")
            )
            _logger.debug("invoice has recurring items %s", contract_recurring_items)
            if not contract_recurring_items:
                continue
            result = {"HasNextPage": True}
            page = 0
            while result.get("HasNextPage"):
                result = invoice.env["sumit.account"]._request(
                    "/billing/payments/list",
                    {
                        "Date_From": invoice.invoice_date.isoformat(),
                        "Date_To": (
                            invoice.invoice_date + timedelta(days=1)
                        ).isoformat(),
                        "Valid": True,
                        "StartIndex": page,
                    },
                )
                _logger.debug(result)
                for payment in result.get("Payments", []):
                    if not contract_recurring_items & set(
                        payment.get("RecurringCustomerItemIDs", [])
                    ):
                        continue
                    if payment["Amount"] != invoice.amount_total:
                        continue
                    _logger.info("found matching payment %s", payment)
                    page = -1
                    if invoice.state == "draft":
                        invoice._post()
                    invoice._bankayma_pay()
                    break
                if page == -1:
                    break
                page += 1
            if page != -1:
                _logger.info("no matches found")
