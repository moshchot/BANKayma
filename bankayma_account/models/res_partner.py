# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")
    bankayma_vendor_tax_percentage = fields.Float("Custom tax")
    bankayma_vendor_max_amount = fields.Float("Max amount")
    bankayma_vendor_apply_default_tax = fields.Boolean("Use imposed tax")

    @api.constrains("vat", "country_id")
    def check_vat(self):
        """Defuse vat check for individuals in IL"""
        il = self.env.ref("base.il")
        return super(
            ResPartner, self.filtered(lambda x: x.is_company or x.country_id != il)
        ).check_vat()
