# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _to_sumit_vals(self):
        """Return a dict describing this line for sumit"""
        self.ensure_one()
        return {
            "Quantity": self.quantity,
            "TotalPrice": self.price_total,
            "DocumentCurrency_UnitPrice": None,
            "DocumentCurrency_TotalPrice": None,
            "Description": self.name or None,
            "Item": {
                "ID": None,
                "Name": self.product_id.name or None,
                "Description": None,
                "Price": self.product_id.list_price,
                "Currency": self.env["sumit.account"].sumit_currency(
                    self.move_id.currency_id
                ),
                "Cost": self.product_id.standard_price,
                "ExternalIdentifier": None,
                "SKU": self.product_id.default_code or None,
                "SearchMode": 0,
            },
        }
