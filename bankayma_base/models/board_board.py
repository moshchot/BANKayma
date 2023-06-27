# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class BoardBoard(models.AbstractModel):
    _inherit = "board.board"

    @api.model
    def action_impose_all_users(self):
        dashboard_action = self.env.ref("board.open_board_my_dash_action").sudo()
        view_id = dashboard_action["views"][0][0]
        view = self.env["board.board"].get_view(view_id, "form")
        if self.env.user.has_group("bankayma_base.group_org_manager"):
            self = self.sudo()
        for user in self.env["res.users"].search(
            [("id", "not in", (self.env.user + self.env.ref("base.user_admin")).ids)]
        ):
            self.env["ir.ui.view.custom"].create(
                {
                    "user_id": user.id,
                    "ref_id": view_id,
                    "arch": view["arch"],
                }
            )
