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
        diff = sum(self.mapped("line_ids.line_id.balance")) - sum(
            self.mapped("line_ids.balance")
        )
        if not diff:
            return
        move = self.line_ids.line_id.move_id
        move.write(
            {
                "line_ids": [
                    fields.Command.update(line.line_id.id, {"balance": line.balance})
                    for line in self.line_ids
                    if line.balance != line.line_id.balance
                ]
                + [
                    fields.Command.update(line.id, {"balance": line.balance + diff})
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
