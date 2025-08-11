# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class OperatingUnitCategory(models.Model):
    _inherit = "operating.unit.category"

    available_for_intercompany_invoices = fields.Boolean(default=True)
    available_for_portal = fields.Boolean(default=True)
