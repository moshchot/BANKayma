# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    bankayma_from_company_id = fields.Integer()
    parent_id = fields.Many2one("operating.unit")
