# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_header = fields.Html(translate=True)
    company_details = fields.Html(translate=True)
