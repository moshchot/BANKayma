# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode
from io import StringIO
from operator import attrgetter, itemgetter

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
    export_file_movin = fields.Binary(string="DAT file")
    export_file_movin_name = fields.Char(default="MOVEIN.dat")
    export_map_file_movin = fields.Binary(string="PRM file")
    export_map_file_movin_name = fields.Char(default="MOVEIN.prm")

    export_file_heshin = fields.Binary(string="DAT file")
    export_file_heshin_name = fields.Char(default="HESHIN.dat")
    export_map_file_heshin = fields.Binary(string="PRM file")
    export_map_file_heshin_name = fields.Char(default="HESHIN.prm")

    def button_export(self):
        moves = self.env["account.move"].search(
            [
                ("company_id", "=?", self.company_id.id),
                ("date", ">=", self.date_start),
                ("date", "<=", self.date_end),
                ("state", "=", "posted"),
            ]
        )

        if not moves:
            raise exceptions.UserError(_("No moves found"))

        class ExportRecordMOVIN(Record):
            def __init__(self, **_data):
                super().__init__(
                    (
                        # TODO make configurable
                        F(2, 3, "code"),
                        F(3, 5, "ref1"),
                        F(4, 6, "date_ref"),
                        F(5, 5, "ref2"),
                        F(6, 6, "date_value"),
                        F(7, 3, "currency"),
                        F(8, 22, "details"),
                        F(9, 9, "left_account1"),
                        F(10, 9, "left_account2"),
                        F(11, 9, "right_account1"),
                        F(12, 9, "right_account2"),
                        F(13, 8, "left_account1_amount", float),
                        F(14, 8, "left_account2_amount", float),
                        F(15, 8, "right_account1_amount", float),
                        F(16, 8, "right_account2_amount", float),
                    ),
                    **_data
                )

        class ExportRecordHESHIN(Record):
            def __init__(self, **_data):
                super().__init__(
                    (
                        # TODO make configurable
                        F(2, 15, "key"),
                        F(3, 50, "name"),
                        F(4, 9, "sort_code"),
                        F(5, 5, "filter"),
                    ),
                    **_data
                )

        export_file_movin = OpenformatFile()
        export_map_file_movin = StringIO()
        export_file_heshin = OpenformatFile()
        export_map_file_heshin = StringIO()

        export_map_file_movin.write(
            "%s\r\n" % sum(map(attrgetter("length"), ExportRecordMOVIN()._fields))
        )
        pos = 1
        for field in ExportRecordMOVIN()._fields:
            export_map_file_movin.write(
                "%s %s;%s\r\n" % (pos, pos + field.length - 1, field.code)
            )
            pos += field.length

        export_map_file_heshin.write(
            "%s\r\n" % sum(map(attrgetter("length"), ExportRecordHESHIN()._fields))
        )
        pos = 1
        for field in ExportRecordHESHIN()._fields:
            export_map_file_heshin.write(
                "%s %s;%s\r\n" % (pos, pos + field.length - 1, field.code)
            )
            pos += field.length

        movin_configs = self.env["l10n.il.hashavshevet.config.movin"].search([])
        heshin_configs = self.env["l10n.il.hashavshevet.config.heshin"].search([])
        for move in moves:
            for movin_config in movin_configs:
                if movin_config._eval_field(move, "expr_condition"):
                    export_file_movin.append(
                        ExportRecordMOVIN(**movin_config._eval_all(move))
                    )
            for heshin_config in heshin_configs:
                if heshin_config._eval_field(move, "expr_condition"):
                    record = ExportRecordHESHIN(**heshin_config._eval_all(move))
                    if record not in export_file_heshin.records:
                        export_file_heshin.append(record)

        self.export_file_movin = b64encode(export_file_movin.tobytes())
        self.export_map_file_movin = b64encode(
            export_map_file_movin.getvalue().encode(export_file_movin.encoding)
        )
        self.export_file_heshin = b64encode(export_file_heshin.tobytes())
        self.export_map_file_heshin = b64encode(
            export_map_file_heshin.getvalue().encode(export_file_heshin.encoding)
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

        def format_date(date):
            return date and date.strftime("%d%m%y") or ""

        payments = self.env["account.payment"].browse(
            map(
                itemgetter("account_payment_id"),
                move.invoice_payments_widget
                and move.invoice_payments_widget.get("content")
                or [],
            ),
        )
        payment_ref = payments[:1].ref

        yield ExportRecord(
            code="2",
            ref1=move.name,
            date_ref=format_date(move.invoice_date),
            ref2=payment_ref,
            date_value=format_date(move.bankayma_payment_date),
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
            ref1=(payments[:1].name or "").split("/")[-1],
            date_ref=format_date(move.invoice_date),
            ref2=payment_ref,
            date_value=format_date(move.bankayma_payment_date),
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
