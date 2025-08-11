from datetime import timedelta

from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        default=lambda self: self.env.user._get_default_operating_unit(),
    )

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "date_begin" in result and "date_end" in result:
            result["date_end"] = result["date_begin"] + timedelta(hours=1)
        return result
