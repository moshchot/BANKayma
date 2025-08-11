# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Split created invoices according to bankayma_website_sale_company_id
        """
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)

        moves.operating_unit_id = False
        for line in moves.invoice_line_ids:
            line.operating_unit_id = (
                line.product_id.operating_unit_id or line.move_id.operating_unit_id
            )
        for move in moves:
            ous = move.invoice_line_ids.operating_unit_id
            if len(ous) == 1:
                move.invoice_line_ids.operating_unit_id = ous
                move.operating_unit_id = ous

        return moves

    def _bankayma_checkout_address_required(self):
        return not all(
            product.detailed_type in ("event", "service")
            for product in self.order_line.product_id
        )
