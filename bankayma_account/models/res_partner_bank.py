# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    branch_code = fields.Char(pattern="[0-9]+")
    acc_number = fields.Char(pattern="[0-9]+")

    @api.depends()
    def _compute_lock_trust_fields(self):
        for this in self:
            this.lock_trust_fields = False
