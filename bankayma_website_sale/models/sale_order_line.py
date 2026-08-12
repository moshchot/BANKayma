from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    event_registration_ids = fields.One2many("event.registration", "sale_order_line_id")
