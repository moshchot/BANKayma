# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class L10nIlMasavExport(models.TransientModel):
    _inherit = "l10n.il.masav.export"

    def button_export(self):
        # poison the cache to trick super into using the currently selected company
        if self.env.context.get("lang") != "en_US":
            self = self.with_context(lang="en_US")
        moves = self.env["account.move"].browse(self.env.context.get("active_ids", []))
        moves.read([])
        for move in moves:
            move._cache["company_id"] = self.env.company.id
        return super(L10nIlMasavExport, self).button_export()
