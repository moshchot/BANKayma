# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestOperatingUnitSwitcherJS(HttpCase):
    def test_ui_company_with_ou(self):
        self.start_tour(
            "/odoo?cids=1", "operating_unit_switcher_with_menu", login="admin"
        )

    def test_ui_company_without_ou(self):
        new_company = self.env["res.company"].create(
            {
                "name": "test company",
            }
        )
        self.env.ref("base.user_admin").company_ids += new_company
        self.start_tour(
            f"/odoo?cids={new_company.id}",
            "operating_unit_switcher_without_menu",
            login="admin",
        )
