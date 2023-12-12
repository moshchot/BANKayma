from base64 import b64decode

from odoo.tests.common import TransactionCase


class TestL10nIlSystem1000(TransactionCase):
    def test_export(self):
        wizard = (
            self.env["l10n.il.system1000.export"]
            .with_context(active_ids=self.env["account.move"].search([]).ids)
            .create({})
        )
        wizard.button_export()
        export_data = b64decode(wizard.export_file).decode("iso8859-8").splitlines()
        self.assertTrue(export_data[-1].startswith("Z"))
