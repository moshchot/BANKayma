# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

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
    bankayma_payment_method_id = fields.Many2one(
        "account.payment.method",
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

    @api.depends("journal_id.bankayma_restrict_intercompany_partner")
    def _compute_bankayma_partner_domain(self):
        for this in self:
            if this.journal_id.bankayma_restrict_intercompany_partner:
                this.bankayma_partner_domain = [
                    (
                        "id",
                        "in",
                        self.env["res.company"]
                        .sudo()
                        .search([])
                        .mapped("partner_id.id"),
                    )
                ]
            else:
                this.bankayma_partner_domain = [
                    ("company_id", "in", (False, this.company_id.id))
                ]

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
        """
        Enforce intercompany journal on intercompany invoices,
        mail non-intercompany invoices on post
        """
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
        if self.env.user.has_group("bankayma_base.group_org_manager"):
            to_send = self.filtered(
                lambda x: x.move_type
                in ("in_invoice", "out_invoice", "in_refund", "out_refund")
                and not x.auto_invoice_id
                and not self.search([("auto_invoice_id", "=", x.id)])
            )
            if to_send:
                action = to_send.action_invoice_sent()
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
                    'data-oe-id="%(id)s" href="#">%(name)s</a>'
                )
                % child_invoice
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
                payment_form.communication = "%s: %s" % (
                    this.name,
                    " ".join(this.mapped("invoice_line_ids.name")),
                )
                payment_form.save().action_create_payments()
                if child.overhead_payment_journal_id:
                    payment_form = Form(
                        self.env["account.payment.register"]
                        .with_context(
                            active_id=child_invoice.id,
                            active_ids=child_invoice.ids,
                            active_model=child_invoice._name,
                        )
                        .with_company(child)
                    )
                    payment_form.journal_id = child.overhead_payment_journal_id
                    payment_form.communication = "%s: %s" % (
                        this.name,
                        " ".join(this.mapped("invoice_line_ids.name")),
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

    def _portal_create_vendor_bill(self, post_data, uploaded_files):
        company = self.env["res.company"].browse(
            int(post_data.get("company", self.env.company.id))
        )
        with Form(
            self.with_context(default_move_type="in_invoice").with_company(company)
        ) as invoice_form:
            invoice_form.partner_id = self.env.user.partner_id
            with invoice_form.invoice_line_ids.new() as invoice_line:
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
        return {"type": "ir.actions.act_window.page.next"}
