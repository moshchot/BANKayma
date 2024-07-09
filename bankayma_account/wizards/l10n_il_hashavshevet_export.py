# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nIlHashavshevetExport(models.TransientModel):
    _inherit = "l10n.il.hashavshevet.export"

    journal_ids = fields.Many2many(
        check_company=False,
        domain=lambda self: [("company_id", "=", self.env.company.id)],
    )

    def _get_move_line_domain(self):
        result = super()._get_move_line_domain()
        return [
            leaf
            if leaf[0] != "move_id.journal_id"
            else ("move_id.journal_id.code", "in", self.journal_ids.mapped("code"))
            for leaf in result
        ] + [
            ("move_id.journal_id.intercompany_sale_company_id", "=", False),
            ("move_id.journal_id.intercompany_overhead_company_id", "=", False),
            ("move_id.journal_id.intercompany_purchase_company_id", "=", False),
        ]
