# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    name = fields.Char(
        translate=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        group = self.env.ref("bankayma_base.group_org_manager")
        self.env["res.users"].sudo().search([("groups_id", "=", group.id)]).write(
            {
                "company_ids": [(4, this.id) for this in result],
            }
        )
        return result
