# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo import fields, models


class L10nIlSystem1000Export(models.TransientModel):
    _name = "l10n.il.system1000.export"
    _description = "System 1000 export"

    export_file = fields.Binary(readonly=True)
    export_file_name = fields.Char(readonly=True)

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
        action_dict["res_id"] = self.id
        return action_dict

    def _export_header(self):
        return "A{:>9}".format(self.env.company.l10n_il_tax_deduction_id)

    def _export_lines(self):
        return "\r\n".join(
            self._export_line(line)
            for line in self.env["account.move"].browse(
                self.env.context.get("active_ids", [])
            )
        )

    def _export_line(self, line):
        return "B{:>15}{:0>9}{:0>9}".format(
            line.partner_id.vat,
            line.partner_id.property_account_payable_id.code,
            line.partner_id.property_account_payable_id.code,
        )

    def _export_footer(self):
        return "Z{:>9}{:0>4}".format(
            self.env.company.l10n_il_tax_deduction_id,
            len(self.env.context.get("active_ids", [])),
        )
