# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompanyCategory(models.Model):
    _inherit = "res.company.category"

    name = fields.Char(translate=True)
    show_in_company_selector = fields.Boolean(default=True)
