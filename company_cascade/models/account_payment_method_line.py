# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger("company_cascade")


class AccountPaymentMethodLine(models.Model):
    _inherit = ["account.payment.method.line", "company.cascade.mixin"]
    _name = "account.payment.method.line"
    _company_cascade_force_fields = ("name",)

    company_id = fields.Many2one("res.company", related="journal_id.company_id")

    def _company_cascade_find_candidate(self, company, vals):
        result = self.search(
            [
                ("payment_method_id", "=", vals["payment_method_id"]),
                ("journal_id", "=", vals["journal_id"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        _logger.debug("find_candidate: returning %s", result)
        return result
