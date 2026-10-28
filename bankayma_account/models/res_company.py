# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    overhead_journal_id = fields.Many2one(
        "account.journal",
        "Overhead journal",
        help="Overhead invoices will be created in this journal",
        domain=[("type", "=", "sale")],
    )
    overhead_account_id = fields.Many2one(
        "account.account",
        "Overhead account",
        help="Overhead invoice lines will have this account",
    )
    bankayma_overhead_percentage = fields.Float(
        "Overhead percentage",
        compute="_compute_bankayma_overhead_percentage",
        inverse="_inverse_bankayma_overhead_percentage",
        compute_sudo=True,
        tracking=True,
    )
    donation_journal_id = fields.Many2one(
        "account.journal",
        "Donation journal",
        domain=[("type", "=", "sale")],
    )
    donation_credit_transfer_product_id = fields.Many2one(
        "product.product",
        string="Product for Donations via Credit Transfer",
        domain=[("type", "=", "service")],
        ondelete="restrict",
    )
    inter_ou_journal_id = fields.Many2one(
        "account.journal",
        "Inter OU journal",
        domain=[("type", "=", "general")],
    )
    inter_ou_product_id = fields.Many2one(
        "product.product",
        "Inter OU product",
    )

    def _compute_bankayma_overhead_percentage(self):
        for this in self:
            this.bankayma_overhead_percentage = max(
                self.env["account.journal"]
                .search(
                    [
                        ("bankayma_charge_overhead", "=", True),
                        ("company_id", "=", this.id),
                    ]
                )
                .mapped("bankayma_overhead_percentage")
                or [0]
            )

    def _inverse_bankayma_overhead_percentage(self):
        for this in self:
            self.env["account.journal"].search(
                [
                    ("bankayma_charge_overhead", "=", True),
                    ("company_id", "=", this.id),
                ]
            ).write(
                {
                    "bankayma_overhead_percentage": this.bankayma_overhead_percentage,
                }
            )
