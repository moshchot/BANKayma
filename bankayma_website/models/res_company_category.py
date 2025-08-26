# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompanyCategory(models.Model):
    _inherit = "res.company.category"

    category_show_on_website = fields.Boolean("Show on website", default=True)
    company_hide_without_category = fields.Boolean(
        "Hide without category",
        help="Do not show companies with this category unless the category is "
        "explicitly chosen",
        default=False,
    )
