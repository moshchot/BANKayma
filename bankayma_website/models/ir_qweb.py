from odoo import models


class IrQweb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _prepare_frontend_environment(self, values):
        result = super()._prepare_frontend_environment(values)
        main_object = values.get("main_object")
        if main_object:
            values["bankayma_editable"] = bool(
                main_object.sudo(False)
                .filtered(lambda x: x.check_access_rights("write", False))
                ._filter_access_rules("write")
            )
            if values["bankayma_editable"] and not values.get("translatable"):
                values["translatable"] = (
                    self.env.context.get("lang")
                    != self.env["ir.http"]._get_default_lang().code
                )
        return result
