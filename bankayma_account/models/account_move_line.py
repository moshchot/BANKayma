# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bankayma_parent_move_line_id = fields.Many2one("account.move.line")
    bankayma_immutable = fields.Boolean()

    def _compute_name(self):
        for this in self:
            if this.bankayma_immutable:
                this.name = getattr(this, "_origin", this).name
            else:
                super(AccountMoveLine, this)._compute_name()
        return None

    def _compute_price_unit(self):
        for this in self:
            if this.bankayma_immutable:
                this.price_unit = getattr(this, "_origin", this).price_unit
            else:
                super(AccountMoveLine, this)._compute_price_unit()
        return None
