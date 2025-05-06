# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_group_ids = fields.Many2many("res.groups")
    signup_company_id = fields.Many2one("res.company")
    signup_company_ids = fields.Many2many("res.company")
    signup_login_redirect = fields.Char()
    bankayma_vendor_tax_percentage = fields.Float("Custom tax")
    bankayma_vendor_max_amount = fields.Monetary("Max amount")
    bankayma_vendor_amount_this_year = fields.Monetary(
        "Amount paid this year", compute="_compute_bankayma_vendor_amount_this_year"
    )
    bankayma_tax_group_ids = fields.Many2many(
        "account.tax.group",
        "res_partner_bankayma_tax_group",
        "partner_id",
        "tax_group_id",
        string="Tax groups",
    )
    bankayma_tax_group_id = fields.Many2one(
        "account.tax.group",
        compute="_compute_bankayma_tax_group_id",
        inverse="_inverse_bankayma_tax_group_id",
        search="_search_bankayma_tax_group_id",
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
    total_billed = fields.Monetary(
        compute="_compute_total_billed",
        groups="account.group_account_invoice,account.group_account_readonly",
    )

    def _compute_bankayma_vendor_amount_this_year(self):
        AccountMove = self.env["account.move"]
        year_start = fields.Date.today().replace(month=1, day=1)
        year_end = year_start.replace(month=12, day=31)
        for this in self:
            this.bankayma_vendor_amount_this_year = -sum(
                AccountMove.search(
                    [
                        ("partner_id", "=", this.id),
                        ("move_type", "=", "in_invoice"),
                        ("date", ">=", year_start),
                        ("date", "<=", year_end),
                        ("state", "=", "posted"),
                        ("journal_id.intercompany_purchase_company_id", "=", False),
                        ("journal_id.intercompany_sale_company_id", "=", False),
                        ("journal_id.intercompany_overhead_company_id", "=", False),
                    ]
                ).mapped("amount_total_signed")
            )

    @api.depends("bankayma_tax_group_ids")
    def _compute_bankayma_tax_group_id(self):
        for this in self:
            this.bankayma_tax_group_id = this.bankayma_tax_group_ids[:1]

    def _inverse_bankayma_tax_group_id(self):
        for this in self:
            this.bankayma_tax_group_ids = [
                fields.Command.set(this.bankayma_tax_group_id.ids)
            ]

    def _search_bankayma_tax_group_id(self, operator, value):
        return [("bankayma_tax_group_ids", operator, value)]

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
    def check_vat(self):  # pylint: disable=missing-return
        """Defuse vat check for individuals in IL"""
        il = self.env.ref("base.il")
        for this in self.filtered(lambda x: x.is_company or x.country_id != il):
            super(ResPartner, this).check_vat()

    def action_invite_vendor(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "bankayma_account.action_bankayma_vendor_invite_form",
        )

    def _compute_total_billed(self):
        for this in self:
            this.total_billed = sum(
                self.env["account.move"]
                .search(self._compute_total_billed_domain())
                .mapped("amount_total")
            )

    def _compute_total_billed_domain(self):
        all_children = self.with_context(active_test=False).search(
            [("id", "child_of", self.ids)]
        )
        return [
            ("move_type", "in", ("in_invoice", "in_refund")),
            ("partner_id", "in", all_children.ids),
            ("payment_state", "=", "paid"),
        ]

    def write(self, vals):
        result = super().write(vals)
        if "bankayma_vendor_tax_percentage" in vals:
            for move in self.env["account.move"].search(
                [
                    ("partner_id", "in", self.ids),
                    ("state", "=", "draft"),
                ]
            ):
                move.button_bankayma_vendor_tax_create()
        return result

    def action_view_partner_bills(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "bankayma_account.action_bankayma_group_expense_move"
        )
        action["domain"] = self._compute_total_billed_domain()
        action["context"] = {
            "default_move_type": "out_invoice",
            "move_type": "out_invoice",
            "journal_type": "sale",
            "search_default_unpaid": 1,
        }
        return action
