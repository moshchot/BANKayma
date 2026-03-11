# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def operating_unit_switcher_get_ou_info(self):
        """
        Return the currently accessible OUs, with the default OU sorted first if
        available.
        It's crucial that this function is called after the company switcher has set up
        allowed_company_ids
        """
        default_operating_unit = (
            self.env.user._get_default_operating_unit() or self.env["operating.unit"]
        )
        result = {
            "operating_units": self.env.user.operating_units()
            .sorted(key=lambda x: x == default_operating_unit and -1 or 0)
            .read(["display_name"]),
            "default_operating_unit_id": default_operating_unit.id,
        }
        for ou_vals in result["operating_units"]:
            ou_vals["name"] = ou_vals.pop("display_name")
        return result

    def operating_units(self):
        allowed_ou_ids = self.env.context.get("allowed_ou_ids")
        return (
            super().operating_units()
            if not allowed_ou_ids
            else super().operating_units().filtered(lambda x: x.id in allowed_ou_ids)
        )

    @api.model
    def _get_default_operating_unit(self, uid2=False):
        if "allowed_ou_ids" in self.env.context:
            self.invalidate_recordset(["assigned_operating_unit_ids"])
            self.env.user.invalidate_recordset(["assigned_operating_unit_ids"])
        return super()._get_default_operating_unit(uid2=uid2)
