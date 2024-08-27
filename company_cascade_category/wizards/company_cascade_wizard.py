# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CompanyCascadeWizard(models.TransientModel):
    _inherit = "company.cascade.wizard"
    _description = "Cascade records to child companies"

    category_ids = fields.Many2many(
        "res.company.category",
        string="Categories",
    )

    def action_cascade(self):
        return super(
            CompanyCascadeWizard,
            self.with_context(company_cascade_category_categories=self.category_ids),
        ).action_cascade()
