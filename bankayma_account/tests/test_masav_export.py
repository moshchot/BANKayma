# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.l10n_il_masav.tests import test_l10n_il_masav


class TestMasavExport(test_l10n_il_masav.TestL10nIlMasav):
    def test_export_multiple_companies(self):
        moves = self.env["account.move"].search(
            [("move_type", "=", "in_invoice"), ("state", "=", "posted")]
        )
        self._amend_partners(moves)
        self.user.company_ids = moves.mapped("company_id")
        wizard = (
            self.env["l10n.il.masav.export"]
            .with_user(self.user)
            .with_company(self.user.company_id)
            .with_context(
                active_ids=moves.ids, allowed_company_ids=self.user.company_ids.ids
            )
            .create({})
        )
        wizard.button_export()
