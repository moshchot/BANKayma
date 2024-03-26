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

    def test_org_manager_companies(self):
        group = self.env.ref("bankayma_base.group_org_manager")
        all_companies = self.env["res.company"].search([])
        main_company = self.env.ref("base.main_company")
        user = self.env["res.users"].create(
            {
                "login": "testorgmanager",
                "name": "testorgmanager",
                "groups_id": [(4, group.id)],
            }
        )
        self.assertItemsEqual(user.company_ids, all_companies)
        user = self.env["res.users"].create({"login": "testuser", "name": "testuser"})
        self.assertEqual(user.company_ids, main_company)
        user.write(
            {
                "groups_id": [(4, group.id)],
            }
        )
        self.assertItemsEqual(user.company_ids, all_companies)
        new_company = self.env["res.company"].create({"name": "new company"})
        self.assertItemsEqual(user.company_ids, all_companies + new_company)
