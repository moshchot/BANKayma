# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = ["account.tax", "company.cascade.mixin"]
    _name = "account.tax"


class AccountTaxRepartitionLine(models.Model):
    _inherit = ["account.tax.repartition.line", "company.cascade.mixin"]
    _name = "account.tax.repartition.line"

    def _company_cascade_find_candidate(self, company, vals):
        """Always overwrite the base repartition line"""
        if vals.get("repartition_type") == "base":
            return self.search(
                [
                    ("repartition_type", "=", vals.get("repartition_type")),
                    ("invoice_tax_id", "=", vals.get("invoice_tax_id")),
                    ("refund_tax_id", "=", vals.get("refund_tax_id")),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
        return super()._company_cascade_find_candidate(company, vals)
