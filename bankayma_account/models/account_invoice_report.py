# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .account_move import VALIDATED_STATE_SELECTION


class AccountTax(models.Model):
    _inherit = "account.invoice.report"

    validated_state = fields.Selection(VALIDATED_STATE_SELECTION)

    @api.model
    def _select(self):
        return super()._select() + ", validated_state"
