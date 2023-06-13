# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    @api.model
    def get_bindings(self, model_name):
        result = super().get_bindings(model_name)
        if "company_cascade_parent_id" in self.env[model_name]._fields:
            action = self.env.ref(
                "company_cascade.action_company_cascade_wizard"
            ).read()[0]
            result.setdefault("action", []).append(action)
        return result
