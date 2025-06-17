# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = ["account.tax", "company.cascade.up.mixin"]
    _name = "account.tax"
    _company_cascade_up_unlink = False

    bankayma_vendor_specific = fields.Boolean()

    def _company_cascade_up(self, vals=None):
        self = self.sudo()
        return super()._company_cascade_up(vals=vals)

    def _company_cascade_find_candidate(self, company, vals):
        return self.search(
            [
                ("company_id", "=", company.id),
                ("name", "=", vals.get("name")),
                ("type_tax_use", "=", vals.get("type_tax_use")),
                ("tax_scope", "=", vals.get("tax_scope")),
            ],
            limit=1,
        )
