from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_rendering_context(self, report, docids, data):
        result = super()._get_rendering_context(report, docids, data)
        document = (result.get("docs") or self.env["unknown"])[:1]
        if document and "operating_unit_id" in document._fields:
            ou = document.operating_unit_id
        else:
            ou = self.env["operating.unit"]
        result["ou"] = ou
        return result
