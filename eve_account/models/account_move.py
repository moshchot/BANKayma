# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    bankayma_waive_overhead = fields.Boolean(
        "Waive overhead",
        help="Exceptionally don't charge overhead for this move",
        states={"draft": [("readonly", False)], "posted": [("readonly", True)]},
    )
    invoice_payment_term_id = fields.Many2one(
        domain="['|', ('fixed_date', '=', False), ('fixed_date', '>', current_date)]"
    )

    def _bankayma_invoice_child_income_get_parent_company(self):
        """Get the parent that invoices overhead"""
        company = self.company_id.parent_id
        while company.parent_id:
            company = company.parent_id
        return company

    def _bankayma_invoice_child_income(
        self,
        fraction=0.07,
        post=True,
        pay=True,
    ):
        if self.bankayma_waive_overhead or not fraction:
            self.message_post(
                body=_(
                    "Overhead of %d%% was waived on this move",
                    self.journal_id.bankayma_overhead_percentage,
                )
            )
            return
        return super()._bankayma_invoice_child_income(
            fraction=self.journal_id.bankayma_overhead_percentage / 100,
            post=post,
            pay=pay,
        )

    def _invoice_paid_hook(self):
        for this in self:
            if this.journal_id.bankayma_qweb_template_invoice_paid:
                this.message_post_with_view(
                    this.journal_id.bankayma_qweb_template_invoice_paid,
                    subject=_("[EVE] %(company)s you've been paid! (Ref %(ref)s)")
                    % dict(company=this.company_id.name, ref=this.name),
                    message_type="comment",
                    subtype_id=self.env.ref(
                        "bankayma_account.message_subtype_vendor"
                    ).id,
                )
        return super()._invoice_paid_hook()
