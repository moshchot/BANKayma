# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")
    signup_company_ids = fields.Many2many("res.company")
    bankayma_vendor_tax_percentage = fields.Float("Custom tax")
    bankayma_vendor_max_amount = fields.Float("Max amount")
    bankayma_tax_group_ids = fields.Many2many(
        "account.tax.group",
        "res_partner_bankayma_tax_group",
        "partner_id",
        "tax_group_id",
        string="Tax groups",
    )
    bankayma_deduct_tax = fields.Boolean(
        related="property_account_position_id.bankayma_deduct_tax"
    )
    bankayma_show_tax_deduction = fields.Boolean(
        "Tax deduction",
        compute="_compute_bankayma_show_tax_deduction",
        inverse="_inverse_bankayma_show_tax_deduction",
    )
    bankayma_available_tax_group_ids = fields.Many2many(
        "account.tax.group",
        related="property_account_position_id.optional_tax_group_ids",
    )

    @api.depends("property_account_position_id", "bankayma_vendor_tax_percentage")
    def _compute_bankayma_show_tax_deduction(self):
        for this in self:
            this.bankayma_show_tax_deduction = (
                this.bankayma_deduct_tax and this.bankayma_vendor_tax_percentage
            )

    def _inverse_bankayma_show_tax_deduction(self):
        for this in self:
            this.bankayma_vendor_tax_percentage = (
                this.bankayma_vendor_tax_percentage
                if this.bankayma_show_tax_deduction
                else 0
            )

    @api.constrains("vat", "country_id")
    def check_vat(self):
        """Defuse vat check for individuals in IL"""
        il = self.env.ref("base.il")
        return super(
            ResPartner, self.filtered(lambda x: x.is_company or x.country_id != il)
        ).check_vat()
