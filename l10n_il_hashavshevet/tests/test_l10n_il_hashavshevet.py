from odoo.tests.common import TransactionCase


class TestL10nIlHashavshevet(TransactionCase):
    def test_export(self):
        wizard = self.env["l10n.il.hashavshevet.export"].create({})
        wizard.button_export()
