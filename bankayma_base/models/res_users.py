# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    login_redirect = fields.Char(
        help="After login, the user will be redirected to this page instead of /web or /my"
    )
