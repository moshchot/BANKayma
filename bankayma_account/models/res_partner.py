# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")
    bankayma_vendor_tax_percentage = fields.Float("Custom vendor tax")
    bankayma_vendor_max_amount = fields.Float("Max amount")

    def check_vat(self):
        """Defuse vat check for individuals in IL"""
        il = self.env.ref("base.il")
        return super(
            ResPartner, self.filtered(lambda x: x.is_company or x.country_id != il)
        ).check_vat()
