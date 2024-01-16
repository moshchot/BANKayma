# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBankaymaBase(TransactionCase):
    def test_board_imposition(self):
        with self.assertRaises(AccessError):
            self.env["board.board"].with_user(
                self.env.ref("base.user_demo")
            ).action_impose_all_users()

    def test_edit_vat(self):
        self.assertTrue(self.env.ref("bankayma_base.projman").partner_id.can_edit_vat())
