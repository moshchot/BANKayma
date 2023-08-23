# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class MassEditingWizard(models.TransientModel):
    _inherit = "mass.editing.wizard"

    default_account_id = fields.Many2one("account.account")

    @api.model
    def _insert_field_in_arch(self, line, field, main_xml_group):
        result = super()._insert_field_in_arch(line, field, main_xml_group)
        if field.model == "account.journal" and field.name in (
            "outbound_payment_method_line_ids",
            "inbound_payment_method_line_ids",
        ):
            for field_node in main_xml_group.xpath("//field[@name='%s']" % field.name):
                journal = self.env["account.journal"].browse(
                    self.env.context.get("active_ids", [models.NewId()])[0]
                )
                method_ids = journal.available_payment_method_ids.ids
                field_node.attrib["context"] = json.dumps(
                    {
                        "default_available_payment_method_ids": method_ids,
                        "default_company_id": journal.company_id.id,
                    }
                )
        return result
