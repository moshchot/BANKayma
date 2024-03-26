# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BankaymaMoveChangeCompany(models.TransientModel):
    _name = "bankayma.move.change.company"
    _description = "Change company"

    company_id = fields.Many2one("res.company", required=True)
    current_company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env["account.move"]
        .browse(self.env.context.get("active_ids", []))
        .mapped("company_id")[:1],
    )

    def action_change_company(self):
        def _equivalent(model, _id):
            record = self.env[model].browse(_id).sudo()
            return (
                record.company_id
                and record._company_cascade_get_all(self.company_id).id
                or record.id
            )

        moves = self.env["account.move"].browse(self.env.context.get("active_ids", []))
        for move in moves.filtered(lambda x: x.state == "draft"):
            fiscal_position = move.fiscal_position_id
            journal = move.journal_id
            invoice_lines = move.invoice_line_ids.filtered(
                lambda x: x.display_type != "line_note"
            )
            line_vals = invoice_lines.read(
                [
                    "account_id",
                    "product_id",
                    "name",
                    "analytic_distribution",
                    "quantity",
                    "price_unit",
                    "display_type",
                    "tax_ids",
                ],
                load="_classic_write",
            )
            invoice_lines.write(
                {
                    "display_type": "line_note",
                    "account_id": False,
                    "amount_currency": False,
                    "price_unit": 0,
                    "credit": 0,
                    "debit": 0,
                    "tax_ids": False,
                }
            )
            move.write(
                {
                    "company_id": self.company_id.id,
                    "fiscal_position_id": fiscal_position.sudo()
                    ._company_cascade_get_all(self.company_id)
                    .id,
                    "journal_id": journal.sudo()
                    ._company_cascade_get_all(self.company_id)
                    .id,
                }
            )
            for vals in line_vals:
                _id = vals.pop("id")
                line = invoice_lines.filtered(lambda x: x.id == _id)
                vals["account_id"] = _equivalent("account.account", vals["account_id"])
                vals["tax_ids"] = [
                    _equivalent("account.tax", tax_id) for tax_id in vals["tax_ids"]
                ]
                vals["analytic_distribution"] = {
                    str(_equivalent("account.analytic.account", int(_id))): percentage
                    for _id, percentage in (vals["analytic_distribution"] or {}).items()
                }
                line.write(vals)
