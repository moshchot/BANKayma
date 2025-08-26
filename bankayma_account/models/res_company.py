# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    name = fields.Char(translate=True)
    invoice_auto_validation = fields.Boolean(default=False)
    intercompany_sale_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany sale journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "sale")],
    )
    intercompany_purchase_journal_id = fields.Many2one(
        "account.journal",
        "Intercompany purchase journal",
        help="Intercompany invoices will be forced to this journal",
        domain=[("type", "=", "purchase")],
    )
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
    # TODO this journal is used for all (semi-)automatic intercompany
    # payments, so this should be renamed to intercompany_payment_journal_id
    overhead_payment_journal_id = fields.Many2one(
        "account.journal",
        "Overhead payment journal",
        help="Overhead invoices will be paid in this journal",
        domain=[("type", "=", "bank")],
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
        domain=[("detailed_type", "=", "service")],
        ondelete="restrict",
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
