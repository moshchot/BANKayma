# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(translate=True)
    function = fields.Char(translate=True)
    is_company = fields.Boolean(default=True)
    user_state = fields.Selection(related="user_ids.state")
    vat = fields.Char(pattern="([0-9]+)|(/)")
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
    lang_id = fields.Many2one("res.lang", compute="_compute_lang_id")
    signup_url = fields.Char(compute_sudo=True)
    signup_valid = fields.Boolean(compute_sudo=True)

    def _compute_lang_id(self):
        for this in self:
            this.lang_id = self.env["res.lang"].search(
                [
                    ("code", "=", this.lang),
                ]
            ) or self.env.ref("base.lang_en")

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

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for this in result:
            # this handles multilingual defaults. come of with something better
            if this.city == "Jerusalem":
                this.with_context(lang="he_IL").city = "ירושלים"
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

    def _prepare_display_address(self, without_company=False):
        """Suppress outputting country if asked"""
        address_format, address_args = super()._prepare_display_address(
            without_company=without_company
        )
        if self.env.context.get(
            "bankayma_address_suppress_il"
        ) and self.country_id == self.env.ref("base.il"):
            address_args["country_name"] = ""
        return address_format, address_args

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        Force partner view to bankayma's simplified form for x2x partner fields
        """

        def has_group(group):
            return self.env.user.has_group("bankayma_base." + group)

        if (
            (not view_id or view_id == self.env.ref("base.view_partner_form").id)
            and view_type == "form"
            and not has_group("group_full")
            and (
                has_group("group_user")
                or has_group("group_manager")
                or has_group("group_org_manager")
            )
            and not self.env.context.get("form_view_ref", "").startswith("bankayma")
        ):
            view_id = self.env.ref("bankayma_base.bankayma_partner_form").id

        return super().get_view(view_id=view_id, view_type=view_type, **options)
