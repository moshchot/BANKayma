# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import SETATTR_SOURCES

from odoo.addons.operating_unit.tests.common import OperatingUnitCommon

SETATTR_SOURCES["button_compute_color"] = (
    "/operating_unit_switcher_color/models/operating_unit.py",
)


class TestOperatingUnitSwitcher(OperatingUnitCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attachment = cls.env.ref("operating_unit_switcher_color.attachment_css")

    def test_create(self):
        """
        Test that a new css entry is added when creating a ou
        """
        new_ou = self.env["operating.unit"].create(
            {
                "name": "test ou",
                "code": "OU42",
                "partner_id": self.env["res.partner"]
                .create(
                    {
                        "name": "test ou",
                    }
                )
                .id,
            }
        )
        self.assertIn(f"body[data-ou-id='{new_ou.id}']".encode(), self.attachment.raw)

    def test_button_compute_color(self):
        """
        Test that the compute button assigns a color
        """
        self.ou1.color_navbar_bg = False
        self.ou1.button_compute_color()
        self.assertTrue(self.ou1.color_navbar_bg)
        # test that patch was undone properly
        self.ou1.company_id.write({"name": "test2"})
        self.assertEqual(self.ou1.company_id.name, "test2")
