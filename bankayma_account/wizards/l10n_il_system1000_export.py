# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

from odoo.addons.l10n_il_system1000.system1000_file import (
    System1000FileImport,
    System1000FileImportInvalid,
)


class L10nIlSystem1000Export(models.TransientModel):
    _inherit = "l10n.il.system1000.export"

    failed_move_ids = fields.Many2many("account.move", readonly=True)

    def button_import(self):
        self = self.with_context(mail_notify_force_inbox=True)
        if self.import_file_valid:
            self._import_valid_file()
        if self.import_file_invalid:
            self._import_invalid_file()
        if self.failed_move_ids:
            return {
                "type": "ir.actions.act_window",
                "name": _("Failed System1000 results"),
                "res_model": "account.move",
                "domain": [("id", "in", self.failed_move_ids.ids)],
                "views": [
                    (
                        self.env.ref("bankayma_account.view_failed_sys1k_moves").id,
                        "tree",
                    ),
                    (False, "form"),
                ],
            }

    def _validate_confirm(self, move):
        """Confirm a move, or validate it if under validation"""
        move.invalidate_recordset()
        if move.need_validation or move.review_ids:
            if not move.review_ids:
                move.request_validation()
                move.invalidate_recordset()
            return move.validate_tier()
        else:
            return move.action_post()

    def _reject_cancel(self, move, message=None):
        """Cancel a move, or reject it if under validation"""
        move.invalidate_recordset()
        if move.need_validation or move.review_ids:
            if not move.review_ids:
                move.request_validation()
                move.invalidate_recordset()
            result = move.reject_tier()
            if result and result.get("type") == "ir.actions.act_window":
                return (
                    self.env[result["res_model"]]
                    .with_context(**result["context"])
                    .create(
                        {
                            "comment": message or _("Rejected by System1000"),
                        }
                    )
                    .add_comment()
                )
            else:
                return result
        else:
            return move.button_cancel()

    def _import_valid_file(self):
        valid_data = System1000FileImport(self.import_file_valid)
        for data in valid_data:
            move = (
                self.env["account.move"]
                .search([("id", "=", int(data.document_id))])
                .exists()
            )
            if not move:
                continue
            if move.state != "draft":
                move.message_post(body=_("Not touching non-draft record"))
                continue
            move.message_post_with_view(
                "bankayma_account.system1000_validation_summary",
                values={"validation": data},
            )
            if not data.tax_papers:
                self._reject_cancel(move)
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
                        body=_("Auto submitting from System1000 import, no deduction")
                    )
                    move._portal_remove_tax()
                    self._validate_confirm(move)
            else:
                move.message_post(
                    body=_("Cancelling because move date is out of validity interval")
                )
                self._reject_cancel(move)

    def _import_invalid_file(self):
        invalid_data = System1000FileImportInvalid(self.import_file_invalid)
        for data in invalid_data:
            move = (
                self.env["account.move"]
                .search([("id", "=", int(data.document_id))])
                .exists()
            )
            if not move:
                continue
            if move.state != "draft":
                move.message_post(body=_("Not touching non-draft record"))
                continue
            move.message_post(
                body=_("Cancelling because of error: %s") % data.error_comment
            )
            move.system1000_error_message = data.error_comment
            self.failed_move_ids += move
            self._reject_cancel(move, data.error_comment)
