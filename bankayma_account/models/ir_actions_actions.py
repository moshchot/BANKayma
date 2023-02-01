# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    @api.model
    def get_bindings(self, model_name):
        result = super().get_bindings(model_name)
        if "company.cascade.mixin" in self.env[model_name]._inherit:
            action = self.env.ref(
                "bankayma_account.action_company_cascade_wizard"
            ).read()[0]
            result.setdefault("action", []).append(action)
        return result
