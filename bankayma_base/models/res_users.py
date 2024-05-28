# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    login_redirect = fields.Char(
        help="After login, the user will be redirected to this page instead of /web or /my"
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._ensure_org_manager_companies()
        return result

    def write(self, vals):
        result = super().write(vals)
        if "groups_id" in vals:
            self._ensure_org_manager_companies()
        return result

    def _ensure_org_manager_companies(self):
        """Add all existing companies to users in self that are org managers"""
        all_companies = self.env["res.company"].sudo().search([])
        for this in self:
            if this.has_group("bankayma_base.group_org_manager") and bool(
                all_companies - this.company_ids
            ):
                this.write(
                    {
                        "company_ids": [(6, 0, all_companies.ids)],
                    }
                )
