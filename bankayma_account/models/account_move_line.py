# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import const_eval


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bankayma_parent_move_line_id = fields.Many2one("account.move.line")
    bankayma_product_domain = fields.Binary(compute="_compute_bankayma_product_domain")
    bankayma_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        store=True,
        compute="_compute_bankayma_analytic_account_id",
        string="Analytic Account",
    )
    bankayma_analytic_plan_id = fields.Many2one(
        "account.analytic.plan",
        store=True,
        compute="_compute_bankayma_analytic_account_id",
        string="Analytic Plan",
    )
    bankayma_edit_buffer = fields.Json(compute="_compute_bankayma_edit_buffer")

    def _compute_name(self):
        """
        Don't touch name ever if set
        """
        for this in self:
            value = getattr(this, "_origin", this).name or (
                this.bankayma_edit_buffer or {}
            ).get("name")
            this.name = value

    def _compute_price_unit(self):
        """
        Don't touch unit price if set
        """
        for this in self:
            value = getattr(this, "_origin", this).price_unit or (
                this.bankayma_edit_buffer or {}
            ).get("price_unit")
            if value:
                this.price_unit = value
            else:
                super(AccountMoveLine, this)._compute_price_unit()
        return None

    @api.onchange("name", "price_unit")
    def _compute_bankayma_edit_buffer(self):
        """
        Save first setting of price/name to be able to restore those in compute
        overrides above
        """
        for this in self:
            previous = this.bankayma_edit_buffer or {}
            this.bankayma_edit_buffer = dict(
                name=previous.get("name") or this.name,
                price_unit=previous.get("price_unit") or this.price_unit,
            )

    def _get_computed_taxes(self):
        """
        Impose taxes on invoices and bills
        """
        if not (
            self.move_id.is_sale_document(include_receipts=True)
            or self.move_id.is_purchase_document(include_receipts=True)
        ):
            return super()._get_computed_taxes()
        fpos = self.move_id.fiscal_position_id
        imposed_tax = fpos.bankayma_tax_ids + (
            fpos.optional_tax_group_ids.mapped("tax_ids")
            & self.move_id.partner_id.bankayma_tax_group_ids.mapped("tax_ids").filtered(
                lambda x: x.company_id == self.move_id.company_id
            )
        )
        if fpos.bankayma_deduct_tax and self.move_id.bankayma_vendor_tax_percentage:
            return (
                imposed_tax or super()._get_computed_taxes()
            ) + self.move_id._portal_get_or_create_tax(
                self.move_id.fiscal_position_id,
                self.move_id.bankayma_vendor_tax_percentage,
                create=False,
            )
        else:
            return imposed_tax or super()._get_computed_taxes()

    @api.depends("move_id.journal_id.bankayma_restrict_product_ids")
    def _compute_bankayma_product_domain(self):
        for this in self:
            if this.move_id.journal_id.bankayma_restrict_product_ids:
                this.bankayma_product_domain = [
                    (
                        "id",
                        "in",
                        this.move_id.journal_id.bankayma_restrict_product_ids.ids,
                    )
                ]
            else:
                this.bankayma_product_domain = [
                    this.move_type in ("out_invoice", "out_refund", "out_receipt")
                    and ("sale_ok", "=", True)
                    or ("purchase_ok", "=", True),
                    ("company_id", "in", (False, this.move_id.company_id.id)),
                ]

    @api.depends("analytic_distribution")
    def _compute_bankayma_analytic_account_id(self):
        for this in self:
            if this.analytic_distribution:
                this.bankayma_analytic_account_id = int(
                    list(this.analytic_distribution.keys())[0].split(",")[0]
                )
                this.bankayma_analytic_plan_id = (
                    this.bankayma_analytic_account_id.plan_id
                )
            else:
                this.bankayma_analytic_account_id = False
                this.bankayma_analytic_plan_id = False

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        result = super()._export_rows(fields, _is_toplevel_call=_is_toplevel_call)
        if ["analytic_distribution"] in fields:
            idx = fields.index(["analytic_distribution"])
            AnalyticAccount = self.env["account.analytic.account"]
            for row in result:
                distribution = const_eval(row[idx] or "{}")
                row[idx] = (
                    ", ".join(
                        AnalyticAccount.browse(int(_id)).name for _id in distribution
                    )
                    or ""
                )
        return result

    def _to_sumit_vals(self):
        result = super()._to_sumit_vals()
        result["Description"] = self.name
        result["Item"]["Name"] = (
            f"[{self.account_id.code}] {self.move_id.company_id.name}: "
            f"{self.product_id.name or self.name}"
        )
        return result

    def _prepare_account_move_line(self, dest_move, dest_company):
        result = super()._prepare_account_move_line(dest_move, dest_company)
        result["name"] = self.name
        result["analytic_distribution"] = self._equivalent_analytic_distribution(
            dest_company
        )
        return result

    def _equivalent_analytic_distribution(self, company):
        """
        Return an analytic distribution using the analytic accounts of company
        """
        return {
            record.id: __percentage
            for record, __percentage in (
                (
                    self.env["account.analytic.account"]
                    .browse(int(_id))
                    ._company_cascade_get_all(company),
                    _percentage,
                )
                for _id, _percentage in (self.analytic_distribution or {}).items()
            )
            if record
        }
