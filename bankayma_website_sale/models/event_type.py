from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    registration_single_name = fields.Boolean("Multiple registrations with one name")
