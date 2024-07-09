# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode
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
    export_file_movin = fields.Binary(string="DAT file")
    export_file_movin_name = fields.Char(default="MOVEIN.dat")
    export_map_file_movin = fields.Binary(string="PRM file")
    export_map_file_movin_name = fields.Char(default="MOVEIN.prm")

    export_file_heshin = fields.Binary(string="DAT file")
    export_file_heshin_name = fields.Char(default="HESHIN.dat")
    export_map_file_heshin = fields.Binary(string="PRM file")
    export_map_file_heshin_name = fields.Char(default="HESHIN.prm")

    def button_export(self):
        move_lines = self.env["account.move.line"].search(self._get_move_line_domain())

        if not move_lines:
            raise exceptions.UserError(_("No move lines found"))

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
                        F(9, 8, "left_account1"),
                        F(10, 8, "left_account2"),
                        F(11, 8, "right_account1"),
                        F(12, 8, "right_account2"),
                        F(13, 12, "left_account1_amount", float),
                        F(14, 12, "left_account2_amount", float),
                        F(15, 12, "right_account1_amount", float),
                        F(16, 12, "right_account2_amount", float),
                    ),
                    **_data
                )

        class ExportRecordHESHIN(Record):
            def __init__(self, **_data):
                super().__init__(
                    (
                        # TODO make configurable
                        F(2, 16, "key"),
                        F(3, 50, "name"),
                        F(4, 9, "sort_code"),
                        F(5, 0, None),
                        F(6, 0, None),
                        F(7, 0, None),
                        F(8, 0, None),
                        F(9, 0, None),
                        F(10, 0, None),
                        F(11, 0, None),
                        F(12, 0, None),
                        F(13, 0, None),
                        F(14, 0, None),
                        F(15, 0, None),
                        F(16, 0, None),
                        F(17, 0, None),
                        F(18, 0, None),
                        F(19, 0, None),
                        F(20, 0, None),
                        F(21, 0, None),
                        F(22, 0, None),
                        F(23, 0, None),
                        F(24, 0, None),
                        F(25, 0, None),
                        F(26, 0, None),
                        F(27, 0, None),
                        F(28, 0, None),
                        F(29, 0, None),
                        F(30, 9, "filter"),
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
        for move_line in move_lines:
            for movin_config in movin_configs:
                if movin_config._eval_field(move_line, "expr_condition"):
                    export_file_movin.append(
                        ExportRecordMOVIN(**movin_config._eval_all(move_line))
                    )
            for heshin_config in heshin_configs:
                if heshin_config._eval_field(move_line, "expr_condition"):
                    record = ExportRecordHESHIN(**heshin_config._eval_all(move_line))
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

    def _get_move_line_domain(self):
        return [
            ("move_id.company_id", "=?", self.company_id.id),
            ("move_id.date", ">=", self.date_start),
            ("move_id.date", "<=", self.date_end),
            ("move_id.state", "=", "posted"),
        ] + (
            [("move_id.journal_id", "in", self.journal_ids.ids)]
            if self.journal_ids
            else []
        )
