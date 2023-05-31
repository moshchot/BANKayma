# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestCompanyCascade(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cascading_parent = cls.env.ref("base.main_company")
        cls.account = cls.env["account.account"].create(
            {
                "company_id": cls.cascading_parent.id,
                "name": "Test account for cascading",
                "code": "cascade.code",
            }
        )
        cls.cascading_child = cls.env["res.company"].create(
            {
                "name": "Cascading child",
                "company_cascade_from_parent": True,
                "parent_id": cls.cascading_parent.id,
            }
        )

    def test_cascade(self):
        """Test basic cascading function"""
        self.assertFalse(self.account.company_cascade_child_ids)
        self.env["company.cascade.wizard"].with_context(
            active_model=self.account._name,
            active_id=self.account.id,
            active_ids=self.account.ids,
        ).create({}).action_cascade()
        self.assertEqual(
            self.account.code,
            self.account.company_cascade_child_ids[:1].code,
        )
