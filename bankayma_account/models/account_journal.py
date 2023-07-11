# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"
    _company_cascade_exclude_fields = tuple(
        [
            "intercompany_sale_company_id",
            "intercompany_purchase_company_id",
            "intercompany_overhead_company_id",
        ]
    )

    bankayma_restrict_intercompany_partner = fields.Boolean(
        "Allow only companies",
        help="When this checkbox is activated, only partners of companies in the system "
        "may be used as partner on invoices",
    )
    bankayma_restrict_product_ids = fields.Many2many(
        "product.product",
        string="Allowed products",
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

    def _check_journal_sequence(self):
        """
        Defuse constraint from account_move_name_sequence pertaining to squences' companies
        """
