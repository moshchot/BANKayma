# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(translate=False)
    function = fields.Char(translate=False)
    street = fields.Char(translate=False)
    street2 = fields.Char(translate=False)
    city = fields.Char(translate=False)
