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

    def _validate_confirm(self, move):
        """Confirm a move, or validate it if under validation"""
        if move.need_validation:
            if not move.review_ids:
                move.request_validation()
                move.invalidate_recordset()
            return move.validate_tier()
        else:
            return move.action_post()

    def _reject_cancel(self, move):
        """Cancel a move, or reject it if under validation"""
        return move.button_cancel()

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
            if move.date <= data.date_to and move.date >= data.date_from:
                if data.tax_deduction_income and data.tax_deduction_income != 99:
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
                        self._validate_confirm(move)
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
                elif data.tax_deduction_income == 99:
                    move.message_post(
                        body=_(
                            "Auto submitting from System1000 import, no tax deduction"
                        )
                    )
                    self._validate_confirm(move)
            else:
                move.message_post(
                    body=_("Cancelling because move date is out of validity interval")
                )
                self._reject_cancel(move)

    def _import_invalid_file(self):
        invalid_data = System1000FileImport(self.import_file_invalid)
        for data in invalid_data:
            move = (
                self.env["account.move"]
                .search([("id", "=", int(data.document_id))])
                .exists()
            )
            if not move or move.state != "draft":
                move.message_post(body=_("Not touching non-draft record"))
            move.message_post(
                body=_("Cancelling because move is listed in invalid file")
            )
            self._reject_cancel(move)
