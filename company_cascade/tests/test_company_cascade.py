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

    def _apply_cascade_wizard(self, record, field_names=None):
        self.env["company.cascade.wizard"].with_context(
            active_model=record._name,
            active_id=record.id,
            active_ids=record.ids,
        ).create(
            {
                "field_ids": [
                    (
                        6,
                        0,
                        self.env["ir.model.fields"]
                        .search(
                            [
                                ("model_id.model", "=", record._name),
                                ("name", "in", field_names),
                            ]
                        )
                        .mapped("id"),
                    ),
                ],
            }
        ).action_cascade()

    def test_cascade(self):
        """Test basic cascading function"""
        self.assertFalse(self.account.company_cascade_child_ids)
        self._apply_cascade_wizard(self.account)
        self.assertEqual(
            self.account.code,
            self.account.company_cascade_child_ids[:1].code,
        )

    def test_cascade_translations(self):
        """Test that we propagate translations correctly"""
        self.env["res.lang"]._activate_lang("fr_FR")
        tax = self.env["account.tax"].create({"name": "tax"})
        tax.with_context(lang="fr_FR").name = "impôt"
        self._apply_cascade_wizard(tax)
        child_tax = tax.company_cascade_child_ids[:1]
        self.assertEqual(
            child_tax.name,
            "tax",
        )
        self.assertEqual(
            child_tax.with_context(lang="fr_FR").name,
            "impôt",
        )
        tax.name = "another tax"
        tax.with_context(lang="fr_FR").name = "autre impôt"
        self._apply_cascade_wizard(tax, ["name"])
        self.assertEqual(child_tax.name, "another tax")
        self.assertEqual(child_tax.with_context(lang="fr_FR").name, "autre impôt")
