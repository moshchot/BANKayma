# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from .. import fields as bankayma_base_fields


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    name = bankayma_base_fields.TranslatedComputedChar(related="partner_id.name")
    parent_id = fields.Many2one("operating.unit")
    category_id = fields.Many2one("operating.unit.category")
    tag_ids = fields.Many2many("operating.unit.tag", string="Tags")

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        group = self.env.ref("bankayma_base.group_org_manager")
        self.env["res.users"].sudo().search([("groups_id", "=", group.id)]).write(
            {
                "operating_unit_ids": [fields.Command.link(this.id) for this in result],
            }
        )
        return result
