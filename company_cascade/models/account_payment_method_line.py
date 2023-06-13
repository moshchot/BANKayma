# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMethodLine(models.Model):
    _inherit = ["account.payment.method.line", "company.cascade.mixin"]
    _name = "account.payment.method.line"

    company_id = fields.Many2one("res.company", related="journal_id.company_id")

    def _company_cascade_find_candidate(self, company, vals):
        return self.search(
            [
                ("name", "=", vals["name"]),
                ("payment_method_id", "=", vals["payment_method_id"]),
                ("journal_id", "=", vals["journal_id"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
