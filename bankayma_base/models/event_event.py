# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .. import fields as bankayma_base_fields


class EventEvent(models.Model):
    _inherit = "event.event"

    city = bankayma_base_fields.TranslatedComputedChar(related="address_id.city")
