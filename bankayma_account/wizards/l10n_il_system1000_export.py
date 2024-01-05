# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

from odoo.addons.l10n_il_system1000.system1000_file import System1000FileImport


class L10nIlSystem1000Export(models.TransientModel):
    _inherit = "l10n.il.system1000.export"

    def button_import(self):
        if self.import_file_valid:
            self._import_valid_file()
        if self.import_file_invalid:
            self._import_invalid_file()

    def _import_valid_file(self):
        valid_data = System1000FileImport(self.import_file_valid)
        for data in valid_data:
            move = (
                self.env["account.move"]
                .search([("id", "=", int(data.document_id))])
                .exists()
            )
            if not move or move.state != "draft":
                move.message_post(body=_("Not touching non-draft record"))
                continue
            move.message_post_with_view(
                "bankayma_account.system1000_validation_summary",
                values={"validation": data},
            )
            if not data.tax_papers:
                continue
            if data.tax_deduction_income and data.tax_deduction_income != 99:
                if move.date <= data.date_to and move.date >= data.date_from:
                    taxes = move.mapped("invoice_line_ids.tax_ids").filtered(
                        "bankayma_vendor_specific"
                    )
                    tax = move._portal_get_or_create_tax(
                        move.company_id,
                        move.fiscal_position_id,
                        data.tax_deduction_income,
                    )
                    if tax in taxes:
                        move.message_post(
                            body=_("Auto submitting from System1000 import")
                        )
                        move._cache["need_validation"] = False
                        move.action_post()
                    else:
                        move.invoice_line_ids.write(
                            {
                                "tax_ids": [
                                    fields.Command.unlink(tax.id) for tax in taxes
                                ]
                                + [fields.Command.link(tax.id)],
                            }
                        )
                        move.message_post(
                            body=_(
                                "Replaced existing tax %(taxes)s with %(tax)s from System1000"
                            )
                            % {
                                "taxes": ", ".join(taxes.mapped("name")),
                                "tax": tax.name,
                            }
                        )
                else:
                    move.message_post(
                        body=_(
                            "Doing nothing because move date is out of validity interval"
                        )
                    )
