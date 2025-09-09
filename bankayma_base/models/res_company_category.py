# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompanyCategory(models.Model):
    _inherit = "res.company.category"

    name = fields.Char(translate=True)
    show_in_company_selector = fields.Boolean(
        help="If this is disabled, companies in this category do not show in the "
        "company selector, unless the user has group organization manager. Those users "
        "see these companies in a collapsed section apart from the other companies",
        default=True,
    )
