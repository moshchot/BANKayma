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
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank journal",
                "type": "bank",
            }
        )
        cls.cascading_child = cls.env["res.company"].create(
            {
                "name": "Cascading child",
                "company_cascade_from_parent": True,
                "parent_id": cls.cascading_parent.id,
            }
        )
        cls.cascading_child_user = cls.env["res.users"].create(
            {
                "login": "cascading child user",
                "name": "cascading child user",
                "company_id": cls.cascading_child.id,
                "company_ids": [(6, 0, cls.cascading_child.ids)],
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
        self._apply_cascade_wizard(self.journal.default_account_id)
        self._apply_cascade_wizard(self.journal.suspense_account_id)
        self._apply_cascade_wizard(self.journal.profit_account_id)
        self._apply_cascade_wizard(self.journal.loss_account_id)
        if "sequence_id" in self.journal._fields:
            self._apply_cascade_wizard(self.journal.sequence_id)
        self._apply_cascade_wizard(self.journal)
        self.assertTrue(self.journal.outbound_payment_method_line_ids)

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

    def test_cascade_many2many(self):
        """Test that we cascade many2many fields with company restricted records"""
        tax = self.env["account.tax"].create(
            {
                "name": "testtax",
                "company_id": self.cascading_parent.id,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "testproduct",
                "company_id": False,
                "taxes_id": [(6, 0, tax.ids)],
            }
        )
        self.env.invalidate_all()
        self.assertFalse(product.with_user(self.cascading_child_user).taxes_id)
        self._apply_cascade_wizard(product, [])
        self.env.invalidate_all()
        self.assertFalse(product.with_user(self.cascading_child_user).taxes_id)
        self._apply_cascade_wizard(tax, [])
        self._apply_cascade_wizard(product, [])
        self.env.invalidate_all()
        self.assertEqual(
            product.with_user(self.cascading_child_user).taxes_id,
            tax.company_cascade_child_ids.filtered(
                lambda x: x.company_id == self.cascading_child
            ),
        )
        self.env.invalidate_all()
        self.assertEqual(
            product.taxes_id.filtered(
                lambda x: x.company_id in (self.cascading_parent + self.cascading_child)
            ),
            tax
            + tax.company_cascade_child_ids.filtered(
                lambda x: x.company_id == self.cascading_child
            ),
        )

    def test_cascade_one2many(self):
        """
        Test that cascading of one2many fields works while finding equivalent records
        """
        tax = self.env["account.tax"].create(
            {
                "name": "testtax",
            }
        )
        fpos = self.env["account.fiscal.position"].create(
            {
                "name": "test",
                "tax_ids": [
                    (0, 0, {"tax_src_id": tax.id}),
                    (0, 0, {"tax_src_id": tax.id, "tax_dest_id": tax.id}),
                ],
            }
        )
        self._apply_cascade_wizard(tax)
        self._apply_cascade_wizard(fpos)
        child = fpos.company_cascade_child_ids
        self.assertEqual(child.company_id, self.cascading_child)
        self.assertItemsEqual(
            child.tax_ids.mapped("company_cascade_parent_id"), fpos.tax_ids
        )
        # break connection, cascading should find it again
        child.tax_ids.write({"company_cascade_parent_id": False})
        self._apply_cascade_wizard(fpos, [])
        self.assertItemsEqual(
            child.tax_ids.mapped("company_cascade_parent_id"), fpos.tax_ids
        )

    def test_cascade_no_company(self):
        """
        Test that cascading many2one fields linking to a record with company_id unset
        doesn't duplicate this record
        """

        def find_all_global_sequences():
            return self.env["ir.sequence"].sudo().search([("company_id", "=", False)])

        sequence = self.env["ir.sequence"].create(
            {"name": "Cross company sequence", "company_id": False}
        )
        all_sequences = find_all_global_sequences()
        self._apply_cascade_wizard(sequence)
        self.assertEqual(all_sequences, find_all_global_sequences())
        journal = self.env["account.journal"].create(
            {
                "name": "Journal with cross company sequence",
                "code": "CROSS",
                "secure_sequence_id": sequence.id,
                "type": "general",
            }
        )
        journal._company_cascade(recursive=True)
        self.assertTrue(journal.company_cascade_child_ids)
        self.assertEqual(
            journal._company_cascade_get_all().mapped("secure_sequence_id"), sequence
        )
        self.assertEqual(all_sequences, find_all_global_sequences())

    def test_property_all_companies(self):
        """Test that setting a property sets it in all companies"""
        fiscal_position = self.env["account.fiscal.position"].create(
            {
                "name": "Fiscal position",
            }
        )
        fiscal_position2 = self.env["account.fiscal.position"].create(
            {
                "name": "Fiscal position2",
            }
        )
        cascading_child2 = self.env["res.company"].create(
            {
                "name": "Cascading child2",
                "company_cascade_from_parent": True,
                "parent_id": self.cascading_parent.id,
            }
        )
        self._apply_cascade_wizard(fiscal_position)
        self._apply_cascade_wizard(fiscal_position2)
        fiscal_position_child1 = fiscal_position._company_cascade_get_all(
            self.cascading_child
        )
        fiscal_position_child2 = fiscal_position._company_cascade_get_all(
            cascading_child2
        )
        fiscal_position2_child1 = fiscal_position2._company_cascade_get_all(
            self.cascading_child
        )
        fiscal_position2_child2 = fiscal_position2._company_cascade_get_all(
            cascading_child2
        )
        self.assertTrue(fiscal_position_child1)
        self.assertNotEqual(fiscal_position, fiscal_position_child1)
        self.assertNotEqual(fiscal_position, fiscal_position_child2)
        self.assertNotEqual(fiscal_position_child1, fiscal_position_child2)
        partner = (
            self.env["res.partner"]
            .with_user(self.cascading_child_user)
            .with_company(self.cascading_child)
            .create(
                {
                    "name": "Partner",
                    "property_account_position_id": fiscal_position_child1.id,
                }
            )
        )
        partner_as_parent = partner.with_user(
            self.env.ref("base.user_root")
        ).with_company(self.cascading_parent)
        self.assertEqual(
            partner_as_parent.property_account_position_id,
            fiscal_position,
        )
        partner_as_child2 = partner.with_user(
            self.env.ref("base.user_root")
        ).with_company(cascading_child2)
        self.assertEqual(
            partner_as_child2.property_account_position_id,
            fiscal_position_child2,
        )
        partner_as_child1 = partner.with_user(self.cascading_child_user).with_company(
            self.cascading_child
        )
        partner_as_child1.property_account_position_id = fiscal_position2_child1
        self.env.invalidate_all()
        self.assertEqual(
            partner_as_parent.property_account_position_id,
            fiscal_position2,
        )
        self.assertEqual(
            partner_as_child2.property_account_position_id,
            fiscal_position2_child2,
        )
        # delete the property, that's different from setting to False
        self.env["ir.property"].search(
            [
                ("company_id", "=", cascading_child2.id),
                ("fields_id.name", "=", "property_account_position_id"),
                ("res_id", "=", "res.partner,%s" % partner.id),
            ]
        ).unlink()
        self.env.invalidate_all()
        self.assertFalse(partner_as_parent.property_account_position_id)
        self.assertFalse(partner.property_account_position_id)
        partner_as_child2.property_account_position_id = fiscal_position_child2
        self.env.invalidate_all()
        self.assertEqual(
            partner_as_parent.property_account_position_id,
            fiscal_position,
        )
        self.assertEqual(
            partner.property_account_position_id,
            fiscal_position_child1,
        )
        partner_as_child2.property_account_position_id = False
        self.env.invalidate_all()
        self.assertFalse(partner_as_parent.property_account_position_id)
        self.assertFalse(partner.property_account_position_id)
        # simulate the case where there's a property in a child, but none in parent
        # and we do a write on the child's property
        partner_as_child1.property_account_position_id = fiscal_position_child1
        property_in_parent = self.env["ir.property"].search(
            [
                ("company_id", "=", self.cascading_parent.id),
                ("fields_id.name", "=", "property_account_position_id"),
                ("res_id", "=", "res.partner,%s" % partner.id),
            ]
        )
        self.env.invalidate_all()
        self.env.cr.execute(
            "update ir_property set company_cascade_parent_id=null "
            "where company_cascade_parent_id in %s;"
            "delete from ir_property where id in %s",
            (tuple(property_in_parent.ids), tuple(property_in_parent.ids)),
        )
        self.env.invalidate_all()
        partner_as_child1.property_account_position_id = fiscal_position2_child1
