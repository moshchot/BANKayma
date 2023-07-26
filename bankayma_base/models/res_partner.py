# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_name(self):
        result = super()._get_name()
        if self.env.context.get("bankayma_partner_address_email") and self.email:
            result = "%s\n%s" % (result, self.email)
        if self.env.context.get("bankayma_partner_address_language") and self.lang:
            result = "%s\n%s" % (
                result,
                dict(self._fields["lang"]._description_selection(self.env))[self.lang],
            )
        if self.env.context.get("bankayma_partner_address_vat") and self.vat:
            result = "%s\n%s" % (result, self.vat)
        return result
