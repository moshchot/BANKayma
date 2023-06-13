# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models


class CompanyCascadeWizard(models.TransientModel):
    _name = "company.cascade.wizard"
    _description = "Cascade records to child companies"

    model_id = fields.Many2one(
        "ir.model",
        default=lambda self: self.env["ir.model"]._get(
            self.env.context.get("active_model", "_unknown")
        ),
    )
    field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields to cascade",
        domain="[('model_id', '=', model_id), ('store', '=', True)]",
        help="Select fields to cascade, otherwise all fields will be cascaded",
    )

    def action_cascade(self):
        if not self.env.user.has_group("base.group_system"):
            raise exceptions.AccessError(_("Only admin can cascade companies"))
        for record in self.env[self.env.context["active_model"]].browse(
            self.env.context["active_ids"]
        ):
            record.sudo()._company_cascade(fields=self.field_ids.mapped("name") or None)
