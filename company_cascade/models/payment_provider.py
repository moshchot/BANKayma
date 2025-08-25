# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = ["payment.provider", "company.cascade.mixin"]
    _name = "payment.provider"

    _company_cascade_force_fields = tuple(["journal_id"])

    journal_id = fields.Many2one(search="_search_journal_id")

    def _search_journal_id(self, operator, value):
        provider_ids = (
            self.env["account.payment.method.line"]
            .search([("journal_id", operator, value)])
            .payment_provider_id.ids
        )
        return [("id", "in", provider_ids)]

    def _company_cascade_find_candidate(self, company, vals):
        return self.search(
            [
                ("code", "=", vals.get("code")),
                ("journal_id", "=", vals.get("journal_id")),
                ("company_id", "=", company.id),
            ],
        )
