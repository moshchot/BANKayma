from datetime import timedelta

from odoo import api, models


class EventEvent(models.Model):
    _inherit = "event.event"

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "date_begin" in result and "date_end" in result:
            result["date_end"] = result["date_begin"] + timedelta(hours=1)
        return result
