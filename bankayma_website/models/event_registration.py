from odoo import fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    website_id = fields.Many2one(related="event_id.website_id")
