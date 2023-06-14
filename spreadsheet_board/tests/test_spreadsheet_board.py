# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import TransactionCase


class TestSpreadsheetBoard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.spreadsheet_group = self.env["spreadsheet.dashboard.group"].create(
            {
                "name": "Test dashboard group",
            }
        )
        self.spreadsheet = self.env["spreadsheet.dashboard"].create(
            {
                "name": "Test spreadsheet",
                "dashboard_group_id": self.spreadsheet_group.id,
            }
        )

    def test_add_to_dashboard(self):
        self.spreadsheet.action_add_to_board()
        view = self.env["board.board"].get_view(
            self.env.ref("board.open_board_my_dash_action").views[0][0],
            "form",
        )
        self.assertIn('view_mode="spreadsheet_board"', view["arch"])
