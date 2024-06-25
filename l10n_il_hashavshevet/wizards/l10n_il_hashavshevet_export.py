# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode
from datetime import date
from io import StringIO
from operator import attrgetter

from odoo import _, exceptions, fields, models

from odoo.addons.l10n_il_openformat.openformat_file import F, OpenformatFile, Record


class L10nIlHashavshevetExport(models.TransientModel):
    _name = "l10n.il.hashavshevet.export"
    _description = "Hashavshevet export"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_start = fields.Date(
        required=True, default=fields.Date.today().replace(month=1, day=1)
    )
    date_end = fields.Date(
        required=True, default=fields.Date.today().replace(month=12, day=31)
    )
    journal_ids = fields.Many2many(
        "account.journal", string="Journals", check_company=True
    )
    export_file = fields.Binary(string="DAT file")
    export_file_name = fields.Char(default="MOVEIN.dat")
    export_map_file = fields.Binary(string="PRM file")
    export_map_file_name = fields.Char(default="MOVEIN.prm")

    def button_export(self):
        moves = self.env["account.move"].search(
            [
                ("company_id", "=?", self.company_id.id),
                ("invoice_date", ">=", self.date_start),
                ("date", "<=", self.date_end),
                ("move_type", "=", "in_invoice"),
                ("state", "=", "posted"),
            ]
        )

        if not moves:
            raise exceptions.UserError(_("No moves found"))

        class ExportRecord(Record):
            def __init__(self, **_data):
                super().__init__(
                    (
                        # TODO make configurable
                        F(2, 3, "code"),
                        F(3, 9, "ref1", int),
                        F(4, 9, "ref2", int),
                        F(5, 10, "date_ref", date),
                        F(6, 10, "date_value", date),
                        F(8, 5, "currency"),
                        F(9, 50, "details"),
                        F(10, 15, "left_account1"),
                        F(11, 15, "left_account2"),
                        F(12, 15, "right_account1"),
                        F(13, 15, "right_account2"),
                        F(14, 9, "left_account1_amount", float),
                        F(15, 9, "left_account2_amount", float),
                        F(16, 9, "right_account1_amount", float),
                        F(17, 9, "right_account2_amount", float),
                    ),
                    **_data
                )

        export_file = OpenformatFile()
        export_map_file = StringIO()

        export_map_file.write(
            "%s\n" % sum(map(attrgetter("length"), ExportRecord()._fields))
        )
        pos = 1
        for field in ExportRecord()._fields:
            export_map_file.write(
                "%s %s ; %s\n" % (pos, pos + field.length - 1, field.code)
            )
            pos += field.length

        for move in moves:
            for record in getattr(self, "_export_move_%s" % move.move_type)(
                move, ExportRecord
            ):
                export_file.append(record)

        self.export_file = b64encode(export_file.tobytes())
        self.export_map_file = b64encode(
            export_map_file.getvalue().encode(export_file.encoding)
        )

        action_dict = self.env["ir.actions.actions"]._for_xml_id(
            "l10n_il_hashavshevet.action_l10n_il_hashavshevet_export"
        )
        action_dict.update(res_id=self.id)
        return action_dict

    def _export_move_in_invoice(self, move, ExportRecord):
        """One line for liabilities, one for assets"""

        def all_of_type(account_type):
            return move.mapped("line_ids").filtered(
                lambda x: x.account_id.account_type == account_type
            )

        def first_of_type(account_type):
            return all_of_type(account_type)[:1]

        yield ExportRecord(
            code="2",
            ref1=move.id,
            ref2=move.id,
            date_ref=move.invoice_date,
            date_value=move.bankayma_payment_date,
            currency=move.currency_id.name,
            details=move.partner_id.name,
            left_account1=first_of_type("expense").account_id.code,
            right_account1=first_of_type("liability_current").account_id.code,
            right_account2=first_of_type("asset_current").account_id.code,
            left_account1_amount=sum(move.mapped("line_ids.debit")),
            right_account1_amount=sum(all_of_type("liability_current").mapped("debit"))
            + sum(all_of_type("expense").mapped("debit")),
            right_account2_amount=sum(all_of_type("asset_current").mapped("debit")),
        )

        yield ExportRecord(
            code="5",
            ref1=move.id,
            ref2=move.id,
            date_ref=move.invoice_date,
            date_value=move.bankayma_payment_date,
            currency=move.currency_id.name,
            details=move.partner_id.name,
            left_account1=first_of_type("liability_payable").account_id.code,
            right_account1=first_of_type("liability_payable").account_id.code,
            right_account2=first_of_type("liability_current").account_id.code,
            left_account1_amount=sum(all_of_type("liability_current").mapped("debit"))
            + sum(all_of_type("expense").mapped("debit")),
            right_account1_amount=move.amount_untaxed_signed,
            right_account2_amount=sum(all_of_type("liability_current").mapped("debit")),
        )
