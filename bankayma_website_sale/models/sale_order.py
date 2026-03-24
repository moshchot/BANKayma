# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Split created invoices according to bankayma_website_sale_company_id
        """
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        result = self.env["account.move"]

        def _equivalent(record, company):
            return record._company_cascade_get_all(company)

        for move in moves:
            companies = move.invoice_line_ids.bankayma_website_sale_company_id
            for company in companies:
                copy_defaults = {
                    "company_id": company.id,
                    "journal_id": _equivalent(move.journal_id, company).id,
                    "fiscal_position_id": _equivalent(
                        move.fiscal_position_id, company
                    ).id,
                    "payment_mode_id": _equivalent(move.payment_mode_id, company).id,
                    "invoice_line_ids": [
                        fields.Command.create(
                            dict(
                                line.copy_data()[0],
                                account_id=_equivalent(line.account_id, company).id,
                                tax_ids=[
                                    fields.Command.set(
                                        [
                                            _equivalent(tax, company).id
                                            for tax in line.tax_ids
                                        ]
                                    )
                                ],
                                tax_repartition_line_id=_equivalent(
                                    line.tax_repartition_line_id, company
                                ).id,
                                sale_line_ids=[
                                    fields.Command.set(line.sale_line_ids.ids)
                                ],
                            )
                        )
                        for line in move.invoice_line_ids
                        if line.bankayma_website_sale_company_id == company
                    ],
                }
                move_data = move.copy_data(copy_defaults)[0]
                move_data.pop("line_ids")
                result += (
                    self.env["account.move"].with_company(company).create(move_data)
                )
                move.invoice_line_ids.filtered(
                    lambda x: x.bankayma_website_sale_company_id == company
                ).unlink()
            if not move.invoice_line_ids:
                move.unlink()
            else:
                result += move
        return result

    def _bankayma_checkout_address_required(self):
        return not all(
            product.detailed_type in ("event", "service")
            for product in self.order_line.product_id
        )
