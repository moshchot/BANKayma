# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form
from odoo.tools import float_utils

from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION

VALIDATED_STATE_SELECTION = [
    ("draft", "Draft"),
    ("needs_validation", "Needs validation"),
    ("validated", "Validated"),
    ("rejected", "Rejected"),
    ("paid", "Paid"),
]


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
    bankayma_move_line_account_id = fields.Many2one(
        related="invoice_line_ids.account_id"
    )
    bankayma_move_line_analytic_distribution = fields.Json(
        related="invoice_line_ids.analytic_distribution"
    )
    analytic_precision = fields.Integer(related="invoice_line_ids.analytic_precision")
    bankayma_partner_vat = fields.Char(related="partner_id.vat")
    bankayma_attachment_ids = fields.One2many(
        "ir.attachment", "res_id", domain=[("res_model", "=", _inherit)]
    )
    bankayma_partner_domain = fields.Binary(compute="_compute_bankayma_partner_domain")
    auto_invoice_ids = fields.One2many("account.move", "auto_invoice_id")
    validated_state = fields.Selection(
        VALIDATED_STATE_SELECTION,
        store=True,
        default="needs_validation",
        compute="_compute_validated_state",
        compute_sudo=True,
    )
    bankayma_intercompany_grouping = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_confirm", "To confirm"),
            ("expected", "Expected"),
            ("paid_out", "Paid (out)"),
            ("paid_in", "Paid (in)"),
        ],
        store=True,
        default="draft",
        compute="_compute_bankayma_intercompany_grouping",
        compute_sudo=True,
    )
    bankayma_payment_state = fields.Selection(
        [("draft", "Draft")] + PAYMENT_STATE_SELECTION,
        store=True,
        compute="_compute_payment_state",
    )
    need_validation = fields.Boolean(compute_sudo=True)
    show_fiscal_position_id = fields.Boolean(compute="_compute_show_fiscal_position_id")
    bankayma_deduct_tax = fields.Boolean(
        related="fiscal_position_id.bankayma_deduct_tax"
    )
    bankayma_deduct_tax_use_max_amount = fields.Boolean(
        related="fiscal_position_id.bankayma_deduct_tax_use_max_amount"
    )
    bankayma_vendor_max_amount = fields.Float(
        related="partner_id.bankayma_vendor_max_amount", readonly=False
    )
    bankayma_vendor_tax_percentage = fields.Float(
        related="partner_id.bankayma_vendor_tax_percentage",
        readonly=False,
    )
    bankayma_vendor_tax_exists = fields.Boolean(
        compute="_compute_bankayma_vendor_tax_exists"
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
                if this.validated
                else "rejected"
                if this.rejected
                else "needs_validation"
                if bool(this.sudo().review_ids)
                else "draft"
            )

    @api.depends("review_ids.status", "payment_state", "state")
    def _compute_bankayma_intercompany_grouping(self):
        for this in self:
            this.bankayma_intercompany_grouping = (
                "paid_in"
                if this.payment_state == "paid" and this.move_type == "in_invoice"
                else "paid_out"
                if this.payment_state == "paid" and this.move_type == "out_invoice"
                else "to_confirm"
                if this.state == "posted" and this.move_type == "in_invoice"
                else "expected"
                if bool(this.sudo().review_ids)
                or this.state == "posted"
                and this.move_type == "out_invoice"
                else "draft"
            )

    @api.depends()
    def _compute_payment_state(self):
        result = super()._compute_payment_state()
        for this in self:
            this.bankayma_payment_state = (
                "draft" if this.state == "draft" else this.payment_state
            )
        return result

    @api.depends("journal_id")
    def _compute_show_fiscal_position_id(self):
        for this in self:
            this.show_fiscal_position_id = (
                not this.journal_id.intercompany_sale_company_id
                and not this.journal_id.intercompany_purchase_company_id
                and not this.journal_id.intercompany_overhead_company_id
                and this.move_type != "out_invoice"
                or self.env.context.get("default_show_fiscal_position_id")
                or self.env.user.has_group("bankayma_base.group_full")
            )

    @api.depends("bankayma_vendor_tax_percentage")
    def _compute_bankayma_vendor_tax_exists(self):
        for this in self:
            this.bankayma_vendor_tax_exists = self._portal_get_or_create_tax(
                this.company_id,
                this.fiscal_position_id,
                this.bankayma_vendor_tax_percentage,
                create=False,
            )

    @api.depends("reviewer_ids", "state")
    def _compute_hide_post_button(self):
        result = super()._compute_hide_post_button()
        for this in self:
            this.hide_post_button |= this.state == "draft" and bool(this.reviewer_ids)
        return result

    def write(self, vals):
        result = super().write(vals)
        if "bankayma_vendor_tax_percentage" in vals:
            self.button_bankayma_vendor_tax_create()
        if "fiscal_position_id" in vals:
            self.mapped("invoice_line_ids")._compute_tax_ids()
        return result

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
                lambda x: x.move_type in ("out_invoice", "in_refund", "out_refund")
                and not x.auto_invoice_id
                and not self.search([("auto_invoice_id", "=", x.id)])
                and not x.journal_id.bankayma_inhibit_mails
            )
            if to_send:
                action = to_send.with_company(
                    to_send[:1].company_id
                ).action_invoice_sent()
                if not isinstance(action["view_id"], int):
                    # this happens if the document layout isn't configured yet
                    return action
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
            intercompany = len(self) == 1 and self._find_company_from_invoice_partner()
            if intercompany:
                # request a review for counterpart of intercompany sales invoice
                self.with_company(intercompany).sudo().filtered(
                    lambda x: x.move_type == "out_invoice"
                    and x.auto_invoice_ids.need_validation
                ).mapped("auto_invoice_ids").request_validation()
                self.filtered(lambda x: not x.is_move_sent).write(
                    {"is_move_sent": True}
                )
                result = {"type": "ir.actions.act_window.page.list"}
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
                invoice_line.name = "%s %s" % (this.name, this.partner_id.name)
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
            child_invoice.invoice_line_ids.write(
                {"name": "%s %s" % (this.name, this.partner_id.name)}
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
        portal_product = self.env.ref("bankayma_account.product_portal")
        if any(
            product == portal_product
            for product in self.mapped("invoice_line_ids.product_id")
        ):
            raise UserError(_("Please set up proper product to request validation"))
        result = super().request_validation()
        self.invalidate_recordset(["review_ids"])
        self.env.add_to_compute(self._fields["validated_state"], self)
        self.env.add_to_compute(self._fields["bankayma_intercompany_grouping"], self)
        self._recompute_recordset(["validated_state", "bankayma_intercompany_grouping"])
        return result

    def _portal_create_vendor_bill(self, post_data, uploaded_files):
        company = self.env["res.company"].browse(
            int(post_data.get("company", self.env.company.id))
        )
        fpos = (
            self.env["account.fiscal.position"]
            .browse(int(post_data.get("fpos")))
            ._company_cascade_get_all(company=company)
        )
        with Form(
            self.with_context(
                default_move_type="in_invoice",
                default_show_fiscal_position_id=True,
            ).with_company(company)
        ) as invoice_form:
            invoice_form.partner_id = self.env.user.partner_id
            invoice_form.fiscal_position_id = fpos
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.env.ref(
                    "bankayma_account.product_portal"
                )
                invoice_line.name = post_data.get("description")
                invoice_line.price_unit = post_data.get("amount")
            invoice = invoice_form.save()

        if invoice.bankayma_vendor_tax_percentage:
            invoice.button_bankayma_vendor_tax_create()
        invoice.invoice_line_ids.write(
            {
                "bankayma_immutable": True,
            }
        )
        invoice.invoice_line_ids.invalidate_recordset()
        attachments = self.env["ir.attachment"]
        for uploaded_file in uploaded_files.getlist("upload"):
            datas = uploaded_file.stream.read()
            if not datas:
                continue
            attachments += self.env["ir.attachment"].create(
                {
                    "res_model": self._name,
                    "res_id": invoice.id,
                    "datas": b64encode(datas),
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

    def _portal_remove_tax(self):
        """Remove custom taxes from all lines"""
        self.mapped("invoice_line_ids").write(
            {
                "tax_ids": [
                    (3, tax.id)
                    for tax in self.mapped("invoice_line_ids.tax_ids").filtered(
                        "bankayma_vendor_specific"
                    )
                ],
            }
        )

    def _portal_get_or_create_tax(self, company, fpos, tax_percentage, create=True):
        AccountTax = self.env["account.tax"].with_company(company)
        tax_group = fpos.bankayma_deduct_tax_group_id
        return (
            AccountTax.search(
                [
                    ("type_tax_use", "=", "purchase"),
                    ("amount", "=", tax_percentage),
                    ("price_include", "=", True),
                    ("include_base_amount", "=", False),
                    ("is_base_affected", "=", False),
                    ("amount_type", "=", "code"),
                    ("company_id", "=", company.id),
                    ("tax_group_id", "=", tax_group.id),
                    ("bankayma_vendor_specific", "=", True),
                ]
            )
            or create
            and AccountTax.create(
                {
                    "name": _("%(name)s %(percentage)d%%")
                    % {"name": tax_group.name, "percentage": tax_percentage},
                    "type_tax_use": "purchase",
                    "amount": tax_percentage,
                    "price_include": True,
                    "include_base_amount": False,
                    "is_base_affected": False,
                    "amount_type": "code",
                    "invoice_repartition_line_ids": [
                        (0, 0, {"repartition_type": "base"}),
                        (
                            0,
                            0,
                            {
                                "repartition_type": "tax",
                                "account_id": fpos.bankayma_deduct_tax_account_id.id,
                            },
                        ),
                    ],
                    "sequence": -1,
                    "bankayma_vendor_specific": True,
                    "company_id": company.id,
                    "tax_group_id": tax_group.id,
                    "python_compute": "result = quantity * price_unit * %f"
                    % (tax_percentage / 100),
                }
            )
            or AccountTax
        )

    def button_cancel_unlink(self):
        self.button_cancel()
        self.unlink()
        return {"type": "ir.actions.act_window.page.list"}

    def button_bankayma_vendor_tax_create(self):
        self._portal_get_or_create_tax(
            self.company_id,
            self.fiscal_position_id,
            self.bankayma_vendor_tax_percentage,
        )
        for line in self.invoice_line_ids.filtered(
            lambda x: x.display_type == "product"
        ):
            line._compute_tax_ids()

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + ["validated_state"]

    def action_register_payment(self):
        result = super().action_register_payment()
        result.get("context", {})["dont_redirect_to_payments"] = True
        return result

    def validate_tier(self):
        result = super().validate_tier()
        if result:
            return result
        else:
            return {"type": "ir.actions.act_window.page.list"}

    def _notify_requested_review_body(self):
        return self.env["mail.template"]._render_template_qweb_view(
            "bankayma_account.qweb_template_account_move_draft",
            self._name,
            self.ids,
        )[self.id]

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        product_sumit_types = self.invoice_line_ids.mapped("product_id.sumit_type")
        if len(product_sumit_types) == 1 and all(product_sumit_types):
            result["Details"]["Type"] = product_sumit_types[0]
        return result

    def _invoice_paid_hook(self):
        """Invoice overhead if necessary"""
        for this in self.sudo().with_context(skip_invoice_sync=False):
            if this.journal_id.company_cascade_parent_id.bankayma_charge_overhead:
                parent_journal = this.journal_id.company_cascade_parent_id
                this.with_company(this.company_id)._bankayma_invoice_child_income(
                    fraction=parent_journal.bankayma_overhead_percentage / 100
                )
        return super()._invoice_paid_hook()
