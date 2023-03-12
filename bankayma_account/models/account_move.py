# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tests.common import Form


class AccountMove(models.Model):
    _inherit = "account.move"

    bankayma_amount_paid = fields.Monetary(
        string="Total net paid",
        compute="_compute_amount",
        currency_field="company_currency_id",
        compute_sudo=True,
    )

    def _compute_amount(self):
        """
        Calculate amount paid from amount_residual, but not by summing payment
        transactions as amount_paid does
        """
        result = super()._compute_amount()
        for this in self:
            this.bankayma_amount_paid = (
                this.amount_total_signed - this.amount_residual_signed
            )
        return result

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """Search for moves of all company journals when asked"""
        if self.env.context.get("company_cascade_search_all_journals"):
            AccountJournal = self.env["account.journal"].sudo()
            domain = [
                token
                if not expression.is_leaf(token)
                else token
                if token[0] != "journal_id" or token[1] not in ("=", "in")
                else (
                    "journal_id",
                    "in",
                    AccountJournal.browse(token[2])._company_cascade_get_all().ids,
                )
                for token in domain
            ]
        return super().search(
            domain, offset=offset, limit=limit, order=order, count=count
        )

    def _get_last_sequence_domain(self, relaxed=False):
        """Derive sequence from all moves from sibling/parent companies"""
        where_string, param = super(
            AccountMove,
            self.with_context(company_cascade_search_all_journals=True),
        )._get_last_sequence_domain(relaxed=relaxed)
        if param.get("journal_id"):
            journal = self.env["account.journal"].sudo().browse(param["journal_id"])
            where_string = where_string.replace("journal_id = ", "journal_id in ")
            param["journal_id"] = tuple(journal._company_cascade_get_all().ids)
        return where_string, param

    def action_post(self):
        """Enforce intercompany journal on intercompany invoices"""
        for this in self:
            if (
                this.is_invoice()
                and this._find_company_from_invoice_partner()
                and self.env.context.get("bankayma_force_intercompany_journal", True)
            ):
                if this.is_sale_document():
                    journal = this.company_id.intercompany_sale_journal_id
                else:
                    journal = this.company_id.intercompany_purchase_journal_id
                if journal and this.journal_id != journal:
                    this.journal_id = journal
        result = super().action_post()
        if self.env.user.has_group("bankayma_base.group_user"):
            to_send = self.filtered(
                lambda x: x.move_type
                in ("in_invoice", "out_invoice", "in_refund", "out_refund")
            )
            if to_send:
                result = to_send.action_invoice_sent()
        return result

    def _compute_hide_post_button(self):
        result = super()._compute_hide_post_button()
        for this in self:
            this.hide_post_button |= this.need_validation
        return result

    def _inter_company_create_invoice(self, dest_company):
        """Allow skipping creation of intercompany invoice"""
        if self.env.context.get("skip_intercompany_invoice"):
            return
        return super()._inter_company_create_invoice(dest_company)

    def _bankayma_invoice_child_income(
        self,
        company_id=None,
        fraction=0.07,
        account_code="___10",
        post=True,
        invoice_journal_id=None,
        payment_journal_id=None,
    ):
        """Create invoices for income of child companies"""
        company = (
            company_id
            and self.env["res.company"].browse(company_id)
            or self.env.company
        )
        invoices = self.browse([])
        for child in company.child_ids:
            move_lines = (
                self.env["account.move.line"]
                .with_company(child)
                .search(
                    [
                        ("bankayma_parent_move_line_id", "=", False),
                        ("move_id.move_type", "=", "out_invoice"),
                        ("move_id.state", "=", "posted"),
                        ("credit", ">", 0),
                        ("company_id", "=", child.id),
                    ]
                )
            )
            if not move_lines:
                continue
            account = self.env["account.account"].search(
                [
                    ("code", "like", account_code),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if not account:
                continue
            invoice_form = Form(
                self.env["account.move"]
                .with_context(
                    default_move_type="out_invoice",
                    skip_intercompany_invoice=True,
                    bankayma_force_intercompany_journal=False,
                )
                .with_company(company),
                "account.view_move_form",
            )
            invoice_form.partner_id = child.partner_id
            if invoice_journal_id:
                invoice_form.journal_id = self.env["account.journal"].browse(
                    invoice_journal_id
                )
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.account_id = account
                invoice_line.price_unit = sum(move_lines.mapped("credit")) * fraction
            invoice = invoice_form.save()
            move_lines.write(
                {"bankayma_parent_move_line_id": invoice.invoice_line_ids[:1].id}
            )
            if post:
                invoice.action_post()
                if payment_journal_id:
                    payment_form = Form(
                        self.env["account.payment.register"]
                        .with_context(
                            active_id=invoice.id,
                            active_ids=invoice.ids,
                            active_model=invoice._name,
                        )
                        .with_company(company)
                    )
                    payment_form.journal_id = self.env["account.journal"].browse(
                        payment_journal_id
                    )
                    payment_form.save().action_create_payments()
            invoices += invoice
        return invoices

    def request_validation(self):
        """Set invoice_date before rquesting validation"""
        for this in self:
            if this.is_invoice(include_receipts=True) and not this.invoice_date:
                this.invoice_date = fields.Date.context_today(this)
        return super().request_validation()
