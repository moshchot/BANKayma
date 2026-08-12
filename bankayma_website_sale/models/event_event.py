from datetime import timedelta

from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_multi_qty = fields.Boolean(
        compute="_compute_registration_multi_qty", store=True, readonly=False
    )

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "date_begin" in result and "date_end" in result:
            result["date_end"] = result["date_begin"] + timedelta(hours=1)
        return result

    @api.depends("event_type_id")
    def _compute_registration_multi_qty(self):
        for this in self:
            this.registration_multi_qty = this.event_type_id.registration_multi_qty
