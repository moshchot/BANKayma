# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompanyCategory(models.Model):
    _inherit = "res.company.category"

    available_for_intercompany_invoices = fields.Boolean(default=True)
    available_for_portal = fields.Boolean(default=True)
