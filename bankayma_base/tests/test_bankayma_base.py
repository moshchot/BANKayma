# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBankaymaBase(TransactionCase):
    def test_board_imposition(self):
        with self.assertRaises(AccessError):
            self.env["board.board"].with_user(
                self.env.ref("base.user_demo")
            ).action_impose_all_users()
