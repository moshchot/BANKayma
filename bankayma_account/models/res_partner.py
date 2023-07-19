# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")

    def _get_name(self):
        if self.env.context.get("show_vat"):
            self = self.with_context(
                bankayma_partner_address_vat=True,
                show_vat=False,
                bankayma_partner_address_email=True,
            )
        return super(ResPartner, self)._get_name()
