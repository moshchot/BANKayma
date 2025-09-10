# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tag_ids = fields.Many2many("res.company.tag", string="Tags")
