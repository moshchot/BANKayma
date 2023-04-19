# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
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

    def _inter_company_create_invoice(self, dest_company):
        """Allow skipping creation of intercompany invoice"""
        if self.env.context.get("skip_intercompany_invoice"):
            return
        return super()._inter_company_create_invoice(dest_company)

    def _prepare_invoice_data(self, dest_company):
        """Enforce the intercompany journals"""
        result = super()._prepare_invoice_data(dest_company)
        if result.get("move_type") in self.get_sale_types():
            result["journal_id"] = dest_company.intercompany_sale_journal_id.id
        elif result.get("move_type") in self.get_purchase_types():
            result["journal_id"] = dest_company.intercompany_purchase_journal_id.id
        return result

    def _bankayma_invoice_child_income(
        self,
        fraction=0.07,
        post=True,
        pay=True,
    ):
        """Create invoices for income if self is eligible"""
        invoices = self.browse([])
        for this in self.filtered(
            lambda x: x.payment_state == "paid"
            and x.move_type == "out_invoice"
            and x.company_id.parent_id
        ):
            company = this.company_id.parent_id
            if not company.overhead_journal_id or not company.overhead_account_id:
                continue
            child = this.company_id
            invoice_form = Form(
                self.env["account.move"]
                .with_context(
                    default_move_type="out_invoice",
                    default_journal_id=company.overhead_journal_id,
                    bankayma_force_intercompany_journal=False,
                )
                .with_company(company),
                "account.view_move_form",
            )
            invoice_form.partner_id = child.partner_id
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.env.ref(
                    "bankayma_account.product_overhead"
                )
                invoice_line.account_id = company.overhead_account_id
                invoice_line.price_unit = this.bankayma_amount_paid * fraction
            invoice = invoice_form.save()
            this.line_ids.filtered("credit").write(
                {"bankayma_parent_move_line_id": invoice.invoice_line_ids[:1].id}
            )
            if post:
                invoice.action_post()
            invoice.message_post(
                body=_(
                    'Overhead invoice for <a data-oe-model="account.move" '
                    'data-oe-id="%(id)s" href="#">%(name)s</a>'
                )
                % this
            )
            this.message_post(
                body=_(
                    'Overhead created in <a data-oe-model="account.move" '
                    'data-oe-id="%(id)s" href="#">%(name)s</a>'
                )
                % invoice
            )
            if pay:
                payment_form = Form(
                    self.env["account.payment.register"]
                    .with_context(
                        active_id=invoice.id,
                        active_ids=invoice.ids,
                        active_model=invoice._name,
                    )
                    .with_company(company)
                )
                payment_form.journal_id = company.overhead_payment_journal_id
                payment_form.save().action_create_payments()
            invoices += invoice
        return invoices

    def request_validation(self):
        """Set invoice_date before rquesting validation"""
        for this in self:
            if this.is_invoice(include_receipts=True) and not this.invoice_date:
                this.invoice_date = fields.Date.context_today(this)
        return super().request_validation()
