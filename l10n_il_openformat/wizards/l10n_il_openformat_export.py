# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models


class L10nIlOpenformatExport(models.TransientModel):
    _name = "l10n.il.openformat.export"
    _description = "OPENFORMAT export"

    company_id = fields.Many2one("res.company", required=True, default=self.env.company)
    date_start = fields.Date(
        required=True, default=fields.Date.today().replace(month=1, day=1)
    )
    date_end = fields.Date(
        required=True, default=fields.Date.today().replace(month=12, day=31)
    )
    export_file = fields.Binary("Download", readonly=True)
    export_file_name = fields.Char(default="OPENFRMT.zip")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for this in self:
            if this.date_start >= this.date_end:
                raise exceptions.ValidationError(
                    _(
                        "Start date needs to be greater than end date",
                    )
                )

    def button_export(self):
        """Do the export"""
