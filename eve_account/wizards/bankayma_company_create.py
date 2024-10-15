# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BankaymaCompanyCreate(models.TransientModel):
    _inherit = "bankayma.company.create"

    template_company_id = fields.Many2one(
        domain=["|", ("parent_id", "=", False), ("parent_id.parent_id", "=", False)],
    )
