# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import models


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _compute_domain_keys(self):
        return super()._compute_domain_keys() + ["allowed_ou_ids"]
