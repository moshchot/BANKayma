from datetime import timedelta

from odoo import api, fields, models
from odoo.tools.image import image_data_uri
from odoo.tools.json import scriptsafe as json_safe


class EventEvent(models.Model):
    _inherit = "event.event"

    cover_image = fields.Image(
        compute=lambda self: self.update({"cover_image": False}),
        inverse="_inverse_cover_image",
    )

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "date_begin" in result and "date_end" in result:
            result["date_end"] = result["date_begin"] + timedelta(hours=1)
        return result

    def _inverse_cover_image(self):
        for this in self:
            data = (
                this.cover_properties
                and json_safe.loads(this.cover_properties)
                or this._default_cover_properties()
            )
            data["background-image"] = "url(%s)" % image_data_uri(
                this.cover_image or this.company_id.bankayma_website_cover
            )
            this.cover_properties = json_safe.dumps(data)
