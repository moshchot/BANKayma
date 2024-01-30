# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _create_user_from_template(self, values):
        result = super()._create_user_from_template(values)
        vals = {}
        if result.partner_id.signup_group_ids:
            vals["groups_id"] = [
                (4, _id) for _id in result.partner_id.signup_group_ids.ids
            ]
        if result.partner_id.signup_company_ids:
            vals.update(
                company_id=result.partner_id.signup_company_ids[0].id,
                company_ids=[(6, 0, result.partner_id.signup_company_ids.ids)],
            )
        if result.partner_id.signup_login_redirect:
            vals.update(login_redirect=result.partner_id.signup_login_redirect)
        result.write(vals)
        return result
