# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestBankaymaBase(TransactionCase):
    def test_board_imposition(self):
        with self.assertRaises(AccessError):
            self.env["board.board"].with_user(
                self.env.ref("base.user_demo")
            ).action_impose_all_users()

    def test_edit_vat(self):
        self.assertTrue(self.env.ref("bankayma_base.projman").partner_id.can_edit_vat())

    def test_org_manager_ous(self):
        group = self.env.ref("bankayma_base.group_org_manager")
        all_ous = self.env["operating.unit"].search([])
        user = self.env["res.users"].create(
            {
                "login": "testorgmanager",
                "name": "testorgmanager",
                "groups_id": [(4, group.id)],
            }
        )
        self.assertItemsEqual(user.operating_unit_ids, all_ous)
        user = self.env["res.users"].create({"login": "testuser", "name": "testuser"})
        self.assertFalse(user.operating_unit_ids)
        user.write(
            {
                "groups_id": [(4, group.id)],
            }
        )
        self.assertItemsEqual(user.operating_unit_ids, all_ous)
        new_ou = self.env["operating.unit"].create(
            {
                "name": "new ou",
                "code": "new.ou",
                "partner_id": self.env["res.partner"].create({"name": "new ou"}).id,
            }
        )
        self.assertItemsEqual(user.operating_unit_ids, all_ous + new_ou)

    def test_inheritance_with_translation(self):
        """
        for translations, odoo injects <span oe-translation.. /> elements in
        view archs, which can interfere with inhertiance depending on the xpath
        """
        View = self.env["ir.ui.view"].with_context(edit_translations=True)
        for view in View.search(
            [
                ("model_data_id.module", "like", "bankayma%"),
                ("type", "=", "qweb"),
                ("inherit_id", "=", False),
                ("inherit_children_ids", "!=", False),
            ]
        ):
            view.get_combined_arch()
