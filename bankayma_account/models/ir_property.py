# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrProperty(models.Model):
    _inherit = ["ir.property", "company.cascade.mixin"]
    _name = "ir.property"
    _company_cascade_cascade_create = True
    _company_cascade_cascade_write = True

    def _company_cascade_values(self, company, vals):
        """Special treatment for value_reference"""
        result = super()._company_cascade_values(company, vals)
        if "value_reference" in result and result["value_reference"]:
            result["value_reference"] = self._company_cascade_value_reference(
                company, None, self.get_by_record()
            )
        return result
