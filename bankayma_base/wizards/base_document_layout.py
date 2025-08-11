# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        compute=lambda self: self.update(
            {
                "operating_unit_id": self.env.ref(
                    "operating_unit.main_operating_unit", raise_if_not_found=False
                )
            }
        ),
    )

    def _get_render_information(self, styles):
        result = super()._get_render_information(styles)
        result["docs"] = self
        return result
