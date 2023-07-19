# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _display_address(self, without_company=False):
        result = super()._display_address(without_company=without_company)
        if self.env.context.get("bankayma_partner_address_vat") and self.vat:
            result = "%s\n%s" % (self.vat, result)
        if self.env.context.get("bankayma_partner_address_email") and self.email:
            result = "%s\n%s" % (self.email, result)
        return result
