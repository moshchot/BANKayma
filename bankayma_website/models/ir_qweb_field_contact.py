from odoo import api, models


class IrQwebFieldContact(models.AbstractModel):
    _inherit = "ir.qweb.field.contact"

    @api.model
    def value_to_html(self, value, options):
        if options.get("bankayma_address_suppress_il"):
            value = value and value.with_context(bankayma_address_suppress_il=True)
        return super().value_to_html(value, options)
