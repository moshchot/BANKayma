# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    operating_unit_id = fields.Many2one("operating.unit")
