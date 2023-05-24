# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bankayma_parent_move_line_id = fields.Many2one("account.move.line")
    bankayma_immutable = fields.Boolean()
    bankayma_product_domain = fields.Binary(compute="_compute_bankayma_product_domain")

    def _compute_name(self):
        for this in self:
            if this.bankayma_immutable:
                this.name = getattr(this, "_origin", this).name
            else:
                super(AccountMoveLine, this)._compute_name()
        return None

    def _compute_price_unit(self):
        for this in self:
            if this.bankayma_immutable:
                this.price_unit = getattr(this, "_origin", this).price_unit
            else:
                super(AccountMoveLine, this)._compute_price_unit()
        return None

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
