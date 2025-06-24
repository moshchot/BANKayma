# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import models

_logger = logging.getLogger("company_cascade")


class AccountFiscalPosition(models.Model):
    _inherit = ["account.fiscal.position", "company.cascade.mixin"]
    _name = "account.fiscal.position"


class AccountFiscalPositionTax(models.Model):
    _inherit = ["account.fiscal.position.tax", "company.cascade.mixin"]
    _name = "account.fiscal.position.tax"

    def _company_cascade_find_candidate(self, company, vals):
        result = self.search(
            [
                (
                    "position_id",
                    "=",
                    self.position_id._company_cascade_get_all(company).id,
                ),
                ("tax_src_id", "=", vals.get("tax_src_id")),
                ("tax_dest_id", "=", vals.get("tax_dest_id")),
            ]
        )
        _logger.debug("find_candidate: returning %s", result)
        return result


class AccountFiscalPositionAccount(models.Model):
    _inherit = ["account.fiscal.position.account", "company.cascade.mixin"]
    _name = "account.fiscal.position.account"

    def _company_cascade_find_candidate(self, company, vals):
        result = self.search(
            [
                (
                    "position_id",
                    "=",
                    self.position_id._company_cascade_get_all(company).id,
                ),
                ("account_src_id", "=", vals.get("account_src_id")),
                ("account_dest_id", "=", vals.get("account_dest_id")),
            ]
        )
        _logger.debug("find_candidate: returning %s", result)
        return result
