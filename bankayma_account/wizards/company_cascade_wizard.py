# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class CompanyCascadeWizard(models.TransientModel):
    _name = "company.cascade.wizard"
    _description = "Cascade records to child companies"

    def action_cascade(self):
        if not self.env.user.has_group("base.group_system"):
            raise exceptions.AccessError(_("Only admin can cascade companies"))
        for record in self.env[self.env.context["active_model"]].browse(
            self.env.context["active_ids"]
        ):
            record.sudo()._company_cascade()
