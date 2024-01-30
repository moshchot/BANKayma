# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bankayma_parent_move_line_id = fields.Many2one("account.move.line")
    bankayma_immutable = fields.Boolean(copy=False)
    bankayma_product_domain = fields.Binary(compute="_compute_bankayma_product_domain")
    bankayma_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        store=True,
        compute="_compute_bankayma_analytic_account_id",
        string="Analytic Account",
    )

    def _compute_name(self):
        """
        Don't touch name ever if set
        """
        for this in self:
            if this.name:
                continue
            else:
                super(AccountMoveLine, this)._compute_name()
        return None

    def _compute_price_unit(self):
        """
        Don't touch unit price if line comes from portal
        """
        for this in self:
            if this.bankayma_immutable:
                this.price_unit = getattr(this, "_origin", this).price_unit
            else:
                super(AccountMoveLine, this)._compute_price_unit()
        return None

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
        if self.bankayma_immutable:
            return getattr(self, "_origin", self).tax_ids
        elif fpos.bankayma_deduct_tax and self.move_id.bankayma_vendor_tax_percentage:
            return (
                imposed_tax or super()._get_computed_taxes()
            ) + self.move_id._portal_get_or_create_tax(
                self.move_id.company_id,
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
                    list(this.analytic_distribution.keys())[0]
                )
            else:
                this.bankayma_analytic_account_id = False

    def _to_sumit_vals(self):
        return dict(
            super()._to_sumit_vals(),
            Description="%s, %s, %s, [%s%s]"
            % (
                self.move_id.company_id.name,
                self.name,
                self.move_id.name,
                self.company_id.code,
                self.product_id.code,
            ),
        )
