# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"
    _company_cascade_exclude_fields = tuple(
        [
            "intercompany_sale_company_id",
            "intercompany_purchase_company_id",
            "intercompany_overhead_company_id",
            "intercompany_overhead_payment_company_id",
        ]
    )

    bankayma_restrict_partner = fields.Selection(
        [("no_intercompany", "No intercompany"), ("intercompany", "Only intercompany")],
        "Restrict partners",
        help="Choose one of the values to either force intercompany partners or no "
        "intercompany partners",
    )
    bankayma_restrict_product_ids = fields.Many2many(
        "product.product",
        string="Allowed products",
    )
    bankayma_charge_overhead = fields.Boolean(
        "Charge overhead",
        help="When this is checked, payments for moves in child journals will create an "
        "overhead invoice for the child company",
    )
    bankayma_overhead_percentage = fields.Float(
        "Overhead percentage",
        default=7,
        help="The percentage of the amount to be charged as overhead",
    )
    intercompany_sale_company_id = fields.One2many(
        "res.company",
        "intercompany_sale_journal_id",
    )
    intercompany_purchase_company_id = fields.One2many(
        "res.company",
        "intercompany_purchase_journal_id",
    )
    intercompany_overhead_company_id = fields.One2many(
        "res.company",
        "overhead_journal_id",
    )
    intercompany_overhead_payment_company_id = fields.One2many(
        "res.company",
        "overhead_payment_journal_id",
    )

    def _check_journal_sequence(self):
        """
        Defuse constraint from account_move_name_sequence pertaining to squences' companies
        """

    @api.constrains(
        "bankayma_charge_overhead", "intercompany_overhead_payment_company_id"
    )
    def _check_bankayma_charge_overhead(self):
        for this in self:
            if (
                this.bankayma_charge_overhead
                and this.intercompany_overhead_payment_company_id
            ):
                raise exceptions.ValidationError(
                    _(
                        "You cannot charge overhead on the company's overhead payment journal"
                    )
                )
