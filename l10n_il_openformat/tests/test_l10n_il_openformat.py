from odoo.tests.common import TransactionCase


class TestL10nIlOpenformat(TransactionCase):
    def test_export(self):
        wizard = self.env["l10n.il.openformat.export"].create({})
        wizard.button_export()
