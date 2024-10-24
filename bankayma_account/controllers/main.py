# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields
from odoo.http import request, route
from odoo.osv import expression
from odoo.tools.json import scriptsafe as json_safe

from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    BANKAYMA_EXTRA_FIELDS = ["bank", "bank_branch_code", "bank_acc_number"]

    def __init__(self):
        self.OPTIONAL_BILLING_FIELDS.extend(
            [
                "property_account_position_id",
                "bankayma_vendor_tax_percentage",
                "bankayma_vendor_max_amount",
            ]
            + [
                "tax_group_%d" % tax_group.id
                for tax_group in self._bankayma_get_fiscal_positions().mapped(
                    "optional_tax_group_ids"
                )
            ]
        )
        for optional_field in ("street", "city", "zip", "country_id"):
            if optional_field in self.MANDATORY_BILLING_FIELDS:
                self.MANDATORY_BILLING_FIELDS.remove(optional_field)
            if optional_field not in self.OPTIONAL_BILLING_FIELDS:
                self.OPTIONAL_BILLING_FIELDS.append(optional_field)
        super().__init__()

    def _get_invoices_domain(self):
        result = super()._get_invoices_domain()
        return [
            leaf
            if not expression.is_leaf(leaf) or leaf[0] not in ("state", "is_move_sent")
            else ("state", "!=", "cancel")
            if leaf[0] == "state"
            else expression.TRUE_LEAF
            for leaf in result
        ] + (
            [
                ("partner_id", "=", request.env.user.partner_id.id),
                "|",
                ("move_type", "=", "in_invoice"),
                "&",
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
            ]
            if not request.env.user.has_group("bankayma_base.group_full")
            else []
        )

    def _bankayma_get_fiscal_positions(self):
        return (
            request.env["account.fiscal.position"]
            .sudo()
            .search(
                [
                    ("company_id", "=", request.env.company.id),
                ]
            )
        )

    def _prepare_portal_layout_values(self):
        result = super()._prepare_portal_layout_values()
        result["fiscal_positions"] = self._bankayma_get_fiscal_positions()
        return result

    def _prepare_my_invoices_values(
        self,
        page,
        date_begin,
        date_end,
        sortby,
        filterby,
        domain=None,
        url="/my/invoices",
    ):
        try:
            original_su = request.env.su
            request.env = request.env(su=True)
            result = super()._prepare_my_invoices_values(
                page, date_begin, date_end, sortby, filterby, domain=domain, url=url
            )
        finally:
            request.env = request.env(su=original_su)
        return result

    def on_account_update(self, values, partner):
        for field_name in {"property_account_position_id"} & values.keys():
            try:
                values[field_name] = int(values[field_name])
            except BaseException:
                values[field_name] = False
        fpos = (
            request.env["account.fiscal.position"]
            .sudo()
            .browse(values["property_account_position_id"])
            & self._bankayma_get_fiscal_positions()
        )
        tax_groups = request.env["account.tax.group"].sudo()
        for field_name in values.copy():
            if field_name.startswith("tax_group_"):
                tax_groups += (
                    tax_groups.browse(int(values.pop(field_name)))
                    & fpos.optional_tax_group_ids
                )
        values["bankayma_tax_group_ids"] = [(6, 0, tax_groups.ids)]
        bank_account_fields = ("bank", "bank_branch_code", "bank_acc_number")
        bank_vals = {
            key[len("bank_") :]: request.httprequest.form.get(key)
            for key in bank_account_fields
        }
        if all(bank_vals.values()):
            bank_vals["bank_id"] = int(bank_vals.pop(""))
            accounts = request.env.user.partner_id.sudo().bank_ids
            if accounts:
                values["bank_ids"] = [(1, accounts[:1].id, bank_vals)]
            else:
                values["bank_ids"] = [(0, 0, bank_vals)]
        return values

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(
            {
                key: value
                for key, value in data.items()
                if key not in self.BANKAYMA_EXTRA_FIELDS
            }
        )
        if request.env.user.has_group("bankayma_base.group_vendor"):
            if not data.get("vat") and not request.env.user.partner_id.vat:
                error["vat"] = "error"
                error_message.append(_("The VAT is mandatory for vendors"))
            if not data.get("property_account_position_id"):
                error["property_account_position_id"] = "error"
                error_message.append(_("The fiscal position is mandatory for vendors"))
            if not data.get("bank"):
                error["bank"] = "error"
                error_message.append(_("Banking information is mandatory for vendors"))
            if not data.get("bank_branch_code"):
                error["bank_branch_code"] = "error"
                error_message.append(_("Banking information is mandatory for vendors"))
            if not data.get("bank_acc_number"):
                error["bank_acc_number"] = "error"
                error_message.append(_("Banking information is mandatory for vendors"))
        fpos = (
            request.env["account.fiscal.position"]
            .sudo()
            .browse(int(data.get("property_account_position_id") or 0))
            .exists()
        )
        if fpos.bankayma_deduct_tax and data.get("bankayma_vendor_tax_percentage"):
            if (
                float(data.get("bankayma_vendor_tax_percentage", 0) or 0) < 0
                or float(data.get("bankayma_vendor_tax_percentage", 100) or 100) >= 100
            ):
                error["bankayma_vendor_tax_percentage"] = "error"
                error_message.append(_("Fill in a percentage between 0 and 100"))
        if fpos.bankayma_deduct_tax_use_max_amount:
            if float(data.get("bankayma_vendor_max_amount", 0) or 0) <= 0:
                error["bankayma_vendor_max_amount"] = "error"
                error_message.append(_("Fill in a positive amount"))
        return error, error_message

    def _get_account_searchbar_filters(self):
        result = super()._get_account_searchbar_filters()
        result.update(
            paid={
                "label": _("Paid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("in_payment", "paid")),
                ],
            },
            unpaid={
                "label": _("Unpaid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                ],
            },
            late={
                "label": _("Overdue"),
                "domain": [
                    (
                        "invoice_date_due",
                        "<",
                        fields.Date.context_today(request.env.user),
                    ),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                ],
            },
        )
        if request.env.user.has_group("bankayma_base.group_vendor"):
            result = {
                "all": result["all"],
                "from_me": {
                    "label": _("From me"),
                    "domain": [("move_type", "=", "in_invoice")],
                },
                "to_me": {
                    "label": _("To me"),
                    "domain": [("move_type", "=", "out_invoice")],
                },
            }
        return result

    @route("/my/invoices/new", auth="user", website=True)
    def new_vendor_bill(self, **post):
        vals = self._prepare_portal_layout_values()
        vals["page_name"] = "new_vendor_bill"
        vals["post"] = post
        vals["errors"] = {}
        if post and request.httprequest.method == "POST":
            for field_name in ("amount", "description", "fpos"):
                if not post.get(field_name):
                    vals["errors"][field_name] = True
            fpos = (
                request.env["account.fiscal.position"]
                .sudo()
                .browse(
                    int(post.get("fpos") or 0)
                    or request.env.user.partner_id.property_account_position_id.id
                )
            )
            if not post.get("upload") and fpos.vendor_doc_mandatory:
                vals["errors"]["upload"] = True
            if not vals["errors"]:
                bill = (
                    request.env["account.move"]
                    .sudo()
                    ._portal_create_vendor_bill(
                        post,
                        request.httprequest.files,
                    )
                )
                return request.redirect("/my/invoices/%d" % bill.id)
        return request.render("bankayma_account.portal_new_vendor_bill", vals)

    @route()
    def donation_pay(self, **kwargs):
        """Support recurring payments"""
        options = json_safe.loads(kwargs.get("donation_options", "{}"))
        kwargs["is_recurrent"] = options.get("recurrentPayment") == "true"
        return super().donation_pay(**kwargs)

    def _get_custom_rendering_context_values(self, is_recurrent=False, **kwargs):
        result = super()._get_custom_rendering_context_values(**kwargs)
        result["is_recurrent"] = is_recurrent
        if "partner_details" in result:
            result["partner_details"]["country_id"] = request.env.ref("base.il").id
        return result

    def _create_transaction(
        self,
        payment_option_id,
        reference_prefix,
        amount,
        currency_id,
        partner_id,
        flow,
        tokenization_requested,
        landing_route,
        is_validation=False,
        custom_create_values=None,
        **kwargs
    ):
        result = super()._create_transaction(
            payment_option_id,
            reference_prefix,
            amount,
            currency_id,
            partner_id,
            flow,
            tokenization_requested,
            landing_route,
            is_validation=False,
            custom_create_values=custom_create_values,
            **kwargs
        )

        result.is_recurrent = kwargs.get("is_recurrent")

        return result
