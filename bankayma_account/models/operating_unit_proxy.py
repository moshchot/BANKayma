from odoo import fields, models

from odoo.addons.bankayma_base import fields as bankayma_base_fields


class OperatingUnitProxy(models.Model):
    _name = "operating.unit.proxy"
    _description = "Proxy for operating.unit model"
    _table = "operating_unit"
    _auto = False

    name = bankayma_base_fields.TranslatedComputedChar(related="partner_id.name")
    code = fields.Char()
    partner_id = fields.Many2one("res.partner")

    def _compute_display_name(self):
        return self.env["operating.unit"].__class__._compute_display_name(self)

    def _as_ou(self):
        return self.env["operating.unit"].sudo().browse(self.ids)
