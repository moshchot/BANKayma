# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from lxml import etree

from odoo import models


class SpreadsheetDashboard(models.Model):
    _inherit = "spreadsheet.dashboard"

    def action_add_to_board(self):
        self.ensure_one()
        dashboard_action = self.env.ref("board.open_board_my_dash_action").sudo()
        view_id = dashboard_action["views"][0][0]
        view = self.env["board.board"].get_view(view_id, "form")
        arch = etree.fromstring(view["arch"])
        for column in arch.xpath("//column"):
            etree.SubElement(
                column,
                "action",
                {
                    "name": str(self.id),
                    "string": self.name,
                    "view_mode": "spreadsheet_board",
                },
            )
            break
        self.env["ir.ui.view.custom"].create(
            {
                "user_id": self.env.uid,
                "ref_id": view_id,
                "arch": etree.tostring(arch),
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "reload",
            "params": {
                "action_id": self.env.ref("board.open_board_my_dash_action").id,
            },
        }
