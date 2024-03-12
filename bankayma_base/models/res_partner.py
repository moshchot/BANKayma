# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_company = fields.Boolean(default=True)
    user_state = fields.Selection(related="user_ids.state")

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

    def action_reset_password(self):
        has = self.env.user.has_group
        if (
            has("bankayma_base.group_manager") or has("bankayma_base.group_org_manager")
        ) and not has("base.group_erp_manager"):
            self = self.sudo()
        return self.mapped("user_ids").action_reset_password()

    def can_edit_vat(self):
        """Allow editing vat if there's no vat"""
        return not bool(self.vat) or super().can_edit_vat()
