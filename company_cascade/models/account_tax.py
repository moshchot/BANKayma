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
        """
        As the tax model sets defaults for repartition lines, those are created already
        during cascading, without proper parents. Set them accordingly
        """
        result = super().create(vals_list)
        (
            result.invoice_repartition_line_ids + result.refund_repartition_line_ids
        )._company_cascade_set_parent()
        return result


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
