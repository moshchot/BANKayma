# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import io
import os.path
import zipfile
from base64 import b64encode

from odoo import _, api, exceptions, fields, models

from ..openformat_file import (
    OpenformatFile,
    RecordDataClose,
    RecordDataDocument,
    RecordDataOpen,
    RecordInit,
    RecordInitSummary,
)


class L10nIlOpenformatExport(models.Model):
    _name = "l10n.il.openformat.export"
    _description = "OPENFORMAT export"
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    date_start = fields.Date(
        required=True, default=fields.Date.today().replace(month=1, day=1)
    )
    date_end = fields.Date(
        required=True, default=fields.Date.today().replace(month=12, day=31)
    )
    export_timestamp = fields.Datetime()
    export_file = fields.Binary("Download", readonly=True)
    export_file_name = fields.Char(
        compute=lambda self: [
            this.update({"export_file_name": "OPENFRMT.zip"}) for this in self
        ]
    )

    def name_get(self):
        return [
            (this.id, "%s %s" % (this.company_id.name, this.create_date))
            for this in self
        ]

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for this in self:
            if this.date_start >= this.date_end:
                raise exceptions.ValidationError(
                    _(
                        "Start date needs to be greater than end date",
                    )
                )

    def _export_ini(
        self,
        stream,
        b100_count=0,
        b110_count=0,
        c100_count=0,
        d110_count=0,
        d120_count=0,
        m100_count=0,
    ):
        ini_file = OpenformatFile()
        company = self.company_id
        module = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "l10n_il_openformat")])
        )
        export_timestamp = self.export_timestamp
        ini_file.append(
            RecordInit(
                code="A000",
                bkmvdata_count=b100_count
                + b110_count
                + c100_count
                + d110_count
                + d120_count
                + m100_count
                + 2,
                authorized_dealer_number=company.vat,
                primary_id=self.id,
                software_name="Odoo",
                software_release=module.latest_version,
                software_manufacturer="OCA",
                software_period=2,
                software_save_path="database",
                software_accounting_type=2,
                company_registry_number=company.company_registry,
                company_decuction_file_id=company.l10n_il_tax_deduction_id,
                company_name=company.name,
                company_street=company.street,
                # TODO install partner_street_name for this?
                # company_street_number
                company_city=company.city,
                company_zip=company.zip,
                date_start=self.date_start,
                date_end=self.date_end,
                date_export=export_timestamp.date(),
                time_export=export_timestamp.hour * 100 + export_timestamp.minute,
                charset=1,  # iso
                compressor_name="zip",
                branches=1,  # no branches
                currency=company.currency_id.name,
            )
        )
        ini_file.append(RecordInitSummary(code="B100", count=b100_count))
        ini_file.append(RecordInitSummary(code="B110", count=b110_count))
        ini_file.append(RecordInitSummary(code="C100", count=c100_count))
        ini_file.append(RecordInitSummary(code="D110", count=d110_count))
        ini_file.append(RecordInitSummary(code="D120", count=d120_count))
        ini_file.append(RecordInitSummary(code="M100", count=m100_count))
        stream.write(ini_file.tobytes())

    def _export_data(self, stream):
        data_file = OpenformatFile()
        data_file.append(
            RecordDataOpen(
                primary_id=self.id,
            )
        )

        b100_count = 0
        b110_count = 0
        c100_count = 0
        d110_count = 0
        d120_count = 0
        m100_count = 0

        for record in self._export_data_c100():
            c100_count += 1
            data_file.append(record)

        data_file.append(
            RecordDataClose(
                primary_id=self.id,
                record_count=b100_count
                + b110_count
                + c100_count
                + d110_count
                + d120_count
                + m100_count
                + 2,
            )
        )

        stream.write(data_file.tobytes())
        return dict(
            b100_count=b100_count,
            b110_count=b110_count,
            c100_count=c100_count,
            d110_count=d110_count,
            d120_count=d120_count,
            m100_count=m100_count,
        )

    def _export_data_c100_document_type(self, move):
        return 400 if move.move_type.startswith("in") else 500

    def _export_data_c100(self):
        serial = 0
        for move in self.env["account.move"].search(
            [
                ("date", ">=", self.date_start),
                ("date", "<=", self.date_end),
                ("state", "=", "posted"),
            ]
        ):
            serial += 1
            try:
                yield RecordDataDocument(
                    serial=serial,
                    company_vat=self.company_id.vat,
                    type=self._export_data_c100_document_type(move),
                    number=move.name,
                    create_date=move.create_date.date(),
                    create_time=move.create_date.hour * 100 + move.create_date.minute,
                    partner_name=move.partner_id.name,
                    partner_street=move.partner_id.street,
                    partner_city=move.partner_id.city,
                    partner_zip=move.partner_id.zip,
                    partner_country=move.partner_id.country_id.name,
                    partner_country_code=move.partner_id.country_id.code,
                    partner_phone=move.partner_id.phone,
                    partner_vat=move.partner_id.vat,
                    accounting_date=move.date,
                    amount_tax=move.amount_tax,
                    amount_untaxed=move.amount_untaxed,
                    partner_id=move.partner_id.id,
                    user_id=move.user_id.id,
                    document_id=move.id,
                )
            except ValueError as ex:
                raise exceptions.UserError(
                    _("Error exporting %(move_name)s: %(message)s")
                    % {
                        "move_name": move.name,
                        "message": "".join(ex.args),
                    }
                ) from ex

    def button_export(self):
        """Do the export"""
        self.ensure_one()
        self.export_timestamp = fields.Datetime.now()
        buffer = io.BytesIO()
        path = os.path.join(
            "%s.%s"
            % (
                # is this authorized_dealer_number?
                self.company_id.company_registry,
                self.export_timestamp.strftime("%y"),
            ),
            self.export_timestamp.strftime("%m%d%H%M"),
        )
        with zipfile.ZipFile(buffer, "w") as z:
            with z.open(os.path.join(path, "BKMVDATA.TXT"), "w") as data_file:
                try:
                    record_counts = self._export_data(data_file)
                except ValueError as ex:
                    raise exceptions.UserError("".join(ex.args)) from ex
            with z.open(os.path.join(path, "INI.TXT"), "w") as ini_file:
                try:
                    self._export_ini(ini_file, **record_counts)
                except ValueError as ex:
                    raise exceptions.UserError("".join(ex.args)) from ex
        self.export_file = b64encode(buffer.getbuffer())
