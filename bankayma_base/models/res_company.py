# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from .. import fields as bankayma_base_fields


class ResCompany(models.Model):
    _inherit = "res.company"

    name = bankayma_base_fields.TranslatedComputedChar()
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
