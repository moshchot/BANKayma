from odoo import models
from odoo.http import request


class IrQweb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _prepare_frontend_environment(self, values):
        result = super()._prepare_frontend_environment(values)
        main_object = values.get("main_object")
        if main_object:
            if request and request.cookies.get("ou_ids"):
                main_object = main_object.with_context(
                    allowed_ou_ids=list(map(int, request.cookies["ou_ids"].split("-")))
                )
            values["bankayma_editable"] = bool(
                main_object.sudo(False).filtered(lambda x: x.has_access("write"))
            )
            if values["bankayma_editable"] and not values.get("translatable"):
                values["translatable"] = (
                    self.env.context.get("lang")
                    != self.env["ir.http"]._get_default_lang().code
                )
        return result
