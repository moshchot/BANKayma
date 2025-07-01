# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import lxml

from odoo import api, fields, models


class CompanyCascadeMixin(models.AbstractModel):
    _inherit = "company.cascade.mixin"

    company_code = fields.Char()

    @api.model
    def _setup_fields(self):
        if "company_id" in self._fields:
            self._fields["company_code"].related = "company_id.code"
        return super()._setup_fields()

    def _get_view_company_cascade_form(self, arch):
        result = super()._get_view_company_cascade_form(arch)
        for tree in arch.xpath("//field[@name='company_cascade_child_ids']/tree"):
            lxml.etree.SubElement(tree, "field", {"name": "company_code"})
        return result
