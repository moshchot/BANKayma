from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    registration_multi_qty = fields.Boolean("Allow multiple attendees per registration")
