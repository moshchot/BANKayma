# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = ["account.journal", "company.cascade.mixin"]
    _name = "account.journal"

    bankayma_restrict_intercompany_partner = fields.Boolean(
        "Allow only child companies",
        help="When this checkbox is activated, only child companies of this journals company "
        "may be used as partner on invoices",
    )
    bankayma_restrict_product_ids = fields.Many2many(
        "product.product",
        string="Allowed products",
    )

    def _inverse_type(self):
        # defuse this for now, super would try to create a mail alias
        # and fail on unicode-only names
        pass

    def _company_cascade_values(self, company, vals):
        """Take care that bank accounts are cloned to children"""
        bank_account_id = vals.get("bank_account_id")
        if bank_account_id:
            bank_account = self.env["res.partner.bank"].browse(bank_account_id)
            bank_account_company = self.env["res.company"].search(
                [
                    ("partner_id", "=", bank_account.partner_id.id),
                ]
            )
            if bank_account_company and bank_account_company != company:
                child_account = company.partner_id.bank_ids.filtered(
                    lambda x: x.acc_number == bank_account.acc_number
                )
                if not child_account:
                    child_account = (
                        self.env["res.partner.bank"]
                        .with_company(company)
                        .create(
                            bank_account.copy_data(
                                default={
                                    "company_id": company.id,
                                    "partner_id": company.partner_id.id,
                                }
                            )
                        )
                    )
                vals = dict(vals, bank_account_id=child_account.id)
        return super()._company_cascade_values(company, vals)
