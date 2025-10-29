from odoo import fields, models
from odoo.tools.json import scriptsafe as json_safe


class WebsiteCoverPropertiesMixin(models.AbstractModel):
    _inherit = "website.cover_properties.mixin"

    cover_image = fields.Image(
        compute=lambda self: self.update({"cover_image": False}),
        inverse="_inverse_cover_image",
    )

    def _inverse_cover_image(self):
        for this in self:
            attachment = (
                self.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", this._name),
                        ("res_id", "=", this.id),
                        ("res_field", "=", "cover_image"),
                        ("public", "=", True),
                    ]
                )
            )
            if not this.cover_image:
                if attachment:
                    attachment.unlink()
                continue

            if attachment:
                attachment.datas = this.cover_image
                continue

            attachment = (
                self.env["ir.attachment"]
                .sudo()
                .create(
                    {
                        "res_model": this._name,
                        "res_id": this.id,
                        "res_field": "cover_image",
                        "public": True,
                        "datas": this.cover_image,
                        "name": "cover_image",
                    }
                )
            )

            data = (
                this.cover_properties
                and json_safe.loads(this.cover_properties)
                or this._default_cover_properties()
            )
            data["background-image"] = "url(/web/image/%d)" % attachment.id

            this.cover_properties = json_safe.dumps(data)
