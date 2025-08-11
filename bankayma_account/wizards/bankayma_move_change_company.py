#  Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BankaymaMoveChangeCompany(models.TransientModel):
    # TODO: rename to reflect what it does
    _name = "bankayma.move.change.company"
    _description = "Change Operating Unit"

    operating_unit_id = fields.Many2one("operating.unit", required=True)
    current_operating_unit_id = fields.Many2one(
        "operating.unit",
        default=lambda self: (
            self.env["account.move"]
            .browse(self.env.context.get("active_ids", []))
            .mapped("operating_unit_id")[:1]
        ),
    )
    has_nondraft_moves = fields.Boolean(
        default=lambda self: bool(
            self.env["account.move"]
            .browse(self.env.context.get("active_ids", []))
            .filtered(lambda x: x.state != "draft")
        )
    )

    def action_change_operating_unit(self):
        moves = self.env["account.move"].browse(self.env.context.get("active_ids", []))
        moves.operating_unit_id = False
        moves.line_ids.operating_unit_id = self.operating_unit_id
        moves.operating_unit_id = self.operating_unit_id
