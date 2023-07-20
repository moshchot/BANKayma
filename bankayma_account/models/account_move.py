# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo import _, api, exceptions, fields, models
from odoo.tests.common import Form
from odoo.tools import float_utils


class AccountMove(models.Model):
    _inherit = "account.move"

    bankayma_amount_paid = fields.Monetary(
        string="Total net paid",
        compute="_compute_amount",
        currency_field="company_currency_id",
        compute_sudo=True,
    )
    bankayma_payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Payment method",
        compute="_compute_bankayma_payment_method_id",
        store=True,
    )
    bankayma_move_line_name = fields.Char(related="invoice_line_ids.name")
    bankayma_move_line_product_id = fields.Many2one(
        related="invoice_line_ids.product_id"
    )
    bankayma_partner_vat = fields.Char(related="partner_id.vat")
    bankayma_attachment_ids = fields.One2many(
        "ir.attachment", "res_id", domain=[("res_model", "=", _inherit)]
    )
    bankayma_partner_domain = fields.Binary(compute="_compute_bankayma_partner_domain")
    auto_invoice_ids = fields.One2many("account.move", "auto_invoice_id")
    validated_state = fields.Selection(
        [
            ("needs_validation", "Needs validation"),
            ("validated", "Validated"),
            ("paid", "Paid"),
        ],
        store=True,
        default="needs_validation",
        compute="_compute_validated_state",
        compute_sudo=True,
    )
    need_validation = fields.Boolean(compute_sudo=True)

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

    def _search_default_journal(self):
        """React on a context key to choose company's intercompany sale journal"""
        if self.env.context.get("bankayma_internal_move"):
            return self.env.company.intercompany_sale_journal_id
        return super()._search_default_journal()

    @api.depends("payment_state")
    def _compute_show_reset_to_draft_button(self):
        result = super()._compute_show_reset_to_draft_button()
        for this in self:
            this.show_reset_to_draft_button &= this.payment_state != "paid"
        return result

    @api.depends(
        "line_ids.full_reconcile_id.reconciled_line_ids.move_id.payment_id."
        "payment_method_line_id.payment_method_id"
    )
    def _compute_bankayma_payment_method_id(self):
        for this in self:
            this.bankayma_payment_method_id = this.mapped(
                "line_ids.full_reconcile_id.reconciled_line_ids.move_id.payment_id."
                "payment_method_line_id.payment_method_id"
            )[:1]

    @api.depends("journal_id.bankayma_restrict_partner")
    def _compute_bankayma_partner_domain(self):
        for this in self:
            domain = [("company_id", "in", (False, this.company_id.id))]
            if this.journal_id.bankayma_restrict_partner == "intercompany":
                domain += [
                    (
                        "id",
                        "in",
                        self.env["res.company"]
                        .sudo()
                        .search([])
                        .mapped("partner_id.id"),
                    )
                ]
            elif this.journal_id.bankayma_restrict_partner == "no_intercompany":
                domain += [
                    (
                        "id",
                        "not in",
                        self.env["res.company"]
                        .sudo()
                        .search([])
                        .mapped("partner_id.id"),
                    )
                ]
            this.bankayma_partner_domain = domain

    @api.depends("review_ids.status", "payment_state", "state")
    def _compute_validated_state(self):
        for this in self:
            this.validated_state = (
                "paid"
                if this.payment_state == "paid"
                else "validated"
                if this.validated or not this.need_validation
                else "needs_validation"
            )

    def action_post(self):
        """
        Enforce intercompany journal on intercompany invoices,
        mail non-intercompany invoices on post
        """
        for this in self:
            if float_utils.float_is_zero(
                this.amount_total, precision_rounding=self.currency_id.rounding
            ):
                raise exceptions.UserError(
                    _("You cannot post an item with amount zero")
                )
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
        if self.env.user.has_group(
            "bankayma_base.group_org_manager"
        ) or self.env.user.has_group("bankayma_base.group_user"):
            to_send = self.filtered(
                lambda x: x.move_type
                in ("in_invoice", "out_invoice", "in_refund", "out_refund")
                and not x.auto_invoice_id
                and not self.search([("auto_invoice_id", "=", x.id)])
            )
            if to_send:
                action = to_send.with_company(
                    to_send[:1].company_id
                ).action_invoice_sent()
                with Form(
                    self.env[action["res_model"]].with_context(**action["context"]),
                    action["view_id"],
                ) as send_form:
                    send_form.save().send_and_print_action()
                result = {
                    "type": "ir.actions.act_url",
                    "target": "self",
                    "url": to_send[:1].get_portal_url(),
                }
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
                invoice_line.name = this.name
            invoice = invoice_form.save()
            this.line_ids.filtered("credit").write(
                {"bankayma_parent_move_line_id": invoice.invoice_line_ids[:1].id}
            )
            if post:
                invoice.action_post()
                if pay:
                    invoice._bankayma_pay(
                        journal=invoice.company_id.overhead_payment_journal_id
                    )
            invoice.message_post(
                body=_(
                    'Overhead invoice for <a data-oe-model="account.move" '
                    'data-oe-id="%(id)s" href="#">%(name)s</a>'
                )
                % this
            )
            child_invoice = self.search([("auto_invoice_id", "=", invoice.id)])
            this.message_post(
                body=_(
                    'Overhead created in <a data-oe-model="account.move" '
                    'data-oe-id="%(id)s" href="#">%(ref)s</a>'
                )
                % child_invoice
            )
            if post:
                child_invoice.action_post()
                if pay:
                    child_invoice._bankayma_pay(
                        journal=child_invoice.company_id.overhead_payment_journal_id
                    )

            invoices += invoice
        return invoices

    def _bankayma_pay(self, journal=None, payment_communication=None):
        """Pay an invoice with the payment register wizard"""
        for this in self:
            action = this.action_register_payment()
            payment_form = Form(
                self.env[action["res_model"]]
                .with_context(**action["context"])
                .with_company(this.company_id)
            )
            if journal:
                payment_form.journal_id = journal
            if payment_communication:
                payment_form.communication = payment_communication
            payment_form.save().action_create_payments()

    def request_validation(self):
        """Set invoice_date before rquesting validation"""
        for this in self:
            if this.is_invoice(include_receipts=True) and not this.invoice_date:
                this.invoice_date = fields.Date.context_today(this)
        return super().request_validation()

    def _portal_create_vendor_bill(self, post_data, uploaded_files):
        company = self.env["res.company"].browse(
            int(post_data.get("company", self.env.company.id))
        )
        with Form(
            self.with_context(default_move_type="in_invoice").with_company(company)
        ) as invoice_form:
            invoice_form.partner_id = self.env.user.partner_id
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.env.ref(
                    "bankayma_account.product_portal"
                )
                invoice_line.name = post_data.get("description")
                invoice_line.price_unit = post_data.get("amount")
            invoice = invoice_form.save()
        invoice.fiscal_position_id = self.env["account.fiscal.position"].browse(
            int(post_data.get("fpos"))
        )
        invoice.invoice_line_ids.write({"bankayma_immutable": True})
        attachments = self.env["ir.attachment"]
        for uploaded_file in uploaded_files.getlist("upload"):
            attachments += self.env["ir.attachment"].create(
                {
                    "res_model": self._name,
                    "res_id": invoice.id,
                    "datas": b64encode(uploaded_file.stream.read()),
                    "store_fname": uploaded_file.filename,
                    "name": uploaded_file.filename,
                }
            )
        if attachments:
            invoice.with_context(no_new_invoice=True).message_post(
                body=_("Attachments"),
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                attachment_ids=attachments.ids,
            )
        return invoice

    def button_cancel_unlink(self):
        self.button_cancel()
        self.unlink()
        return {"type": "ir.actions.act_window.page.list"}

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + ["validated_state"]
