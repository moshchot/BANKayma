# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bankayma_to_operating_unit_ids = fields.One2many(
        "operating.unit", "bankayma_from_company_id"
    )
