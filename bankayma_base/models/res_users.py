# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    login_redirect = fields.Char(
        help="After login, the user will be redirected to this page instead of /web or /my"
    )

    @api.depends("groups_id")
    def _compute_share(self):  # pylint: disable=missing-return
        super()._compute_share()
        internal_groups = self.env.ref("bankayma_base.group_income")
        self.filtered(lambda x: x.groups_id & internal_groups).share = False
