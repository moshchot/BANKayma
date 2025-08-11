from odoo import fields, models


class BankaymaMoveEditTaxTotals(models.TransientModel):
    _name = "bankayma.move.edit.tax.totals"
    _description = "Edit tax totals"

    line_ids = fields.One2many("bankayma.move.edit.tax.totals.line", "wizard_id")

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "line_ids" in fields_list and "line_ids" not in result:
            moves = self.env["account.move"].browse(
                self.env.context.get("active_ids", [])
            )
            result["line_ids"] = [
                fields.Command.create(
                    {
                        "line_id": line.id,
                        "balance": line.balance,
                    }
                )
                for line in moves.mapped("line_ids").filtered(
                    lambda x: x.tax_line_id.tax_group_id.bankayma_editable
                )
            ]
        return result

    def action_edit_tax_totals(self):
        diff_included = {}
        diff_excluded = 0.0
        for line in self.line_ids:
            if line.line_id.tax_line_id.price_include:
                diff_included[line.line_id] = line.line_id.balance - line.balance
            else:
                diff_excluded += line.line_id.balance - line.balance
        if not diff_included and not diff_excluded:
            return

        move = self.line_ids.line_id.move_id

        product_lines = []
        for tax_line, diff in diff_included.items():
            sum_prices = move.currency_id.round(
                sum(move.invoice_line_ids.mapped("price_unit"))
            )
            if not sum_prices:
                continue
            for product_line in move.invoice_line_ids.filtered(
                lambda x, tax_line=tax_line: tax_line.tax_line_id in x.tax_ids
            ):
                weighted_diff = diff * product_line.price_unit / sum_prices
                for _dummy, product_line_id, vals in product_lines:
                    if product_line_id == product_line.id:
                        vals["balance"] += weighted_diff
                        vals["price_subtotal"] += weighted_diff
                        break
                else:
                    product_lines.append(
                        fields.Command.update(
                            product_line.id,
                            {
                                "balance": product_line.balance + weighted_diff,
                                "price_subtotal": product_line.price_subtotal
                                + weighted_diff,
                            },
                        )
                    )

        move.write(
            {
                "line_ids": product_lines
                + [
                    fields.Command.update(line.line_id.id, {"balance": line.balance})
                    for line in self.line_ids
                    if line.balance != line.line_id.balance
                ]
                + [
                    fields.Command.update(
                        line.id, {"balance": line.balance + diff_excluded}
                    )
                    for line in move.line_ids
                    if line.account_id.account_type
                    in ("liability_payable", "asset_receivable")
                ]
            }
        )


class BankaymaMoveEditTaxTotalsLine(models.TransientModel):
    _name = "bankayma.move.edit.tax.totals.line"
    _description = "Edit tax totals line"

    wizard_id = fields.Many2one(
        "bankayma.move.edit.tax.totals", required=True, ondelete="cascade"
    )
    line_id = fields.Many2one("account.move.line", required=True, ondelete="cascade")
    balance = fields.Monetary("Amount")
    currency_id = fields.Many2one(related="line_id.currency_id")
    name = fields.Char(related="line_id.name")
