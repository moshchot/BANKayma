# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

_logger = logging.getLogger("company_cascade")


class AccountTax(models.Model):
    _inherit = ["account.tax", "company.cascade.mixin"]
    _name = "account.tax"

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._validate_repartition_lines()
        return result

    def _company_cascade_create(self, values):
        """
        Don't check validity of repartition lines during create, they will be added afterwards
        """
        self = self.with_context(company_cascade_suppress_repartition_check=True)
        return super()._company_cascade_create(values)

    def _company_cascade(self, fields=None, recursive=False, recursive_seen=None):
        result = super()._company_cascade(
            fields=fields, recursive=recursive, recursive_seen=recursive_seen
        )
        result.company_cascade_child_ids._validate_repartition_lines()
        return result

    @api.constrains("invoice_repartition_line_ids", "refund_repartition_line_ids")
    def _validate_repartition_lines(self):
        if self.env.context.get("company_cascade_suppress_repartition_check"):
            return
        return super()._validate_repartition_lines()


class AccountTaxRepartitionLine(models.Model):
    _inherit = ["account.tax.repartition.line", "company.cascade.mixin"]
    _name = "account.tax.repartition.line"

    def _company_cascade_find_candidate(self, company, vals):
        """Always overwrite the base repartition line"""
        result = self.search(
            [
                ("factor_percent", "=", vals.get("factor_percent")),
                ("account_id", "=", vals.get("account_id")),
                ("repartition_type", "=", vals.get("repartition_type")),
                ("invoice_tax_id", "=", vals.get("invoice_tax_id")),
                ("refund_tax_id", "=", vals.get("refund_tax_id")),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        _logger.debug("find_candidate: returning %s", result)
        return result
