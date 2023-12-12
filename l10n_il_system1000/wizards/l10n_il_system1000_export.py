# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo import _, api, fields, models

from ..system1000_file import System1000FileImport


class L10nIlSystem1000Export(models.TransientModel):
    _name = "l10n.il.system1000.export"
    _description = "System 1000 export"

    export_file = fields.Binary(readonly=True)
    export_file_name = fields.Char(readonly=True)
    import_file_valid = fields.Binary()
    import_file_valid_name = fields.Char(default="valid.txt")
    import_file_invalid = fields.Binary()
    import_file_invalid_name = fields.Char(default="invalid.txt")
    import_date = fields.Datetime()
    state = fields.Selection(
        [("draft", "Draft"), ("upload", "Upload Results"), ("done", "Done")],
        compute="_compute_state",
    )

    @api.depends("export_file", "import_file_valid", "import_file_invalid")
    def _compute_state(self):
        for this in self:
            if not any(
                (this.export_file, this.import_file_valid, this.import_file_invalid)
            ):
                this.state = "draft"
            elif this.export_file and not this.import_date:
                this.state = "upload"
            else:
                this.state = "done"

    def button_export(self):
        self.export_file = b64encode(
            (
                self._export_header()
                + "\r\n"
                + self._export_lines()
                + "\r\n"
                + self._export_footer()
            ).encode("ISO-8859-8")
        )
        self.export_file_name = "system1000.txt"
        action_dict = self.env["ir.actions.actions"]._for_xml_id(
            "l10n_il_system1000.action_l10n_il_system1000_export"
        )
        action_dict.update(res_id=self.id, name=_("Upload results"))
        return action_dict

    def _export_header(self):
        return "A{:>9}".format(self.env.company.l10n_il_tax_deduction_id)

    def _export_lines(self):
        return "\r\n".join(
            self._export_line(line)
            for line in self.env["account.move"].browse(
                self.env.context.get("active_ids", [])
            )
            if line.state == "draft"
        )

    def _export_line(self, line):
        return "B{:>15}{:0>9}{:0>9}{:0>9}".format(
            line.id,
            line.partner_id.vat,
            line.partner_id.vat,
            line.partner_id.vat,
        )

    def _export_footer(self):
        return "Z{:>9}{:0>4}".format(
            self.env.company.l10n_il_tax_deduction_id,
            len(self.env.context.get("active_ids", [])),
        )

    def button_import(self):
        valid_data = System1000FileImport(self.import_file_valid)
        # TODO all this is heavily bankayma specific, move there
        for data in valid_data:
            move = (
                self.env["account.move"]
                .search([("id", "=", int(data.document_id))])
                .exists()
            )
            if not move or move.state != "draft":
                continue
            # TODO: remove
            move.message_post(body=repr(data))
            if not data.tax_papers:
                move.message_post(body=_("Doing nothing because #74 is 0"))
                continue
            if data.tax_deduction_income and data.tax_deduction_income != 99:
                if move.date <= data.date_to and move.date >= data.date_from:
                    taxes = move.mapped("invoice_line_ids.tax_ids")
                    tax = move._portal_get_or_create_tax(
                        move.company_id,
                        move.fiscal_position_id,
                        data.tax_deduction_income,
                    )
                    if tax in taxes:
                        # TODO actually do it
                        move.message_post(body=_("This should be auto submitted"))
                    else:
                        # TODO actually do it
                        move.message_post(
                            body=_(
                                "Created a new tax, should replace old vendor specific tax"
                            )
                        )
                else:
                    move.message_post(
                        body=_(
                            "Doing nothing because move date is out of validity interval"
                        )
                    )

        System1000FileImport(self.import_file_invalid)
