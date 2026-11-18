from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    bankayma_overhead_percentage = fields.Float("Overhead Percentage")

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        self.env["account.account"].sudo().search(
            [
                ("is_ou_specific", "=", True),
                (
                    "operating_unit_id",
                    "=",
                    self.env.ref("operating_unit.main_operating_unit").id,
                ),
            ]
        )._create_ou_sibling(result)
        return result
