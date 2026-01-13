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
        return result
