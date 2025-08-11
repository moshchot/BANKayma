# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    login_redirect = fields.Char(
        help="After login, the user will be redirected to this page instead of "
        "/web or /my"
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._ensure_org_manager_ous()
        return result

    def write(self, vals):
        result = super().write(vals)
        if "groups_id" in vals:
            self._ensure_org_manager_ous()
        return result

    def _ensure_org_manager_ous(self):
        """Add all existing ous to users in self that are org managers"""
        all_ous = self.env["operating.unit"].sudo().search([])
        for this in self:
            if this.has_group("bankayma_base.group_org_manager") and bool(
                all_ous - this.operating_unit_ids
            ):
                this.write(
                    {
                        "operating_unit_ids": [
                            fields.Command.link(ou.id)
                            for ou in all_ous
                            if ou not in this.operating_unit_ids
                        ],
                    }
                )

    @api.model
    def operating_unit_switcher_get_ou_info(self):
        """Remove OUs with categories hidden from OU switcher"""
        result = super().operating_unit_switcher_get_ou_info()
        result["hidden_operating_units"] = []
        i = 0
        OperatingUnit = self.env["operating.unit"].sudo()
        while i < len(result["operating_units"]):
            ou_data = result["operating_units"][i]
            ou = OperatingUnit.browse(ou_data["id"])
            if ou.category_id and not ou.category_id.show_in_ou_selector:
                result["operating_units"].pop(i)
                result["hidden_operating_units"].append(ou_data)
                continue
            i += 1
        return result
