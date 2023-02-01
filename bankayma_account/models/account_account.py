# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAccount(models.Model):
    _inherit = ["account.account", "company.cascade.mixin"]
    _name = "account.account"

    def _company_cascade_values(self, company, vals):
        """Add prefix company code if appliccable"""
        result = super()._company_cascade_values(company, vals)
        if result.get("code") and company.parent_id.code and company.code:
            if result["code"].startswith(company.parent_id.code):
                result["code"] = "%s%s" % (
                    company.code,
                    result["code"][len(company.parent_id.code) :],
                )
        return result
