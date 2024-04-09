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
                record_counts = self._export_data(data_file)
            with z.open(os.path.join(path, "INI.TXT"), "w") as ini_file:
                self._export_ini(ini_file, **record_counts)
        self.export_file = b64encode(buffer.getbuffer())
