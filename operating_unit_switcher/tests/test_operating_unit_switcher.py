# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields

from odoo.addons.operating_unit.tests.common import OperatingUnitCommon


class TestOperatingUnitSwitcher(OperatingUnitCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2.operating_unit_ids = cls.ou1 + cls.b2b + cls.b2c

    def test_access(self):
        """
        Test that context key allowed_ou_ids restricts access
        """
        OperatingUnit = self.env["operating.unit"].with_user(self.user2)
        self.assertEqual(
            OperatingUnit.with_context(allowed_ou_ids=self.b2b.ids).search([]),
            self.b2b,
        )
        self.assertItemsEqual(
            OperatingUnit.with_context(allowed_ou_ids=[]).search([]),
            self.b2b + self.b2c + self.ou1,
        )
        self.user2.write(
            {
                "operating_unit_ids": [fields.Command.unlink(self.b2b.id)],
            }
        )
        self.assertEqual(
            OperatingUnit.with_context(allowed_ou_ids=(self.b2c + self.b2b).ids).search(
                []
            ),
            self.b2c,
        )

    def test_ou_info(self):
        """
        Test that default operating unit is sorted first in ou info endpoint
        """
        user = self.user1.with_context(
            allowed_ou_ids=(self.ou1 + self.b2c).ids
        ).with_user(self.user1)
        self.user1.default_operating_unit_id = self.b2c
        ou_info = user.operating_unit_switcher_get_ou_info()
        self.assertEqual(
            ou_info["operating_units"],
            (self.b2c + self.ou1).read(["name"]),
        )
        self.user1.default_operating_unit_id = self.ou1
        ou_info = user.operating_unit_switcher_get_ou_info()
        self.assertEqual(
            ou_info["operating_units"],
            (self.ou1 + self.b2c).read(["name"]),
        )
