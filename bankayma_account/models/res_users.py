# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _create_user_from_template(self, values):
        result = super()._create_user_from_template(values)
        if result.partner_id.signup_group_ids:
            result.groups_id += result.partner_id.signup_group_ids
        return result
