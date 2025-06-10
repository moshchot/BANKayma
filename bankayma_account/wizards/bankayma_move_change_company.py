# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models


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
    has_nondraft_moves = fields.Boolean(
        default=lambda self: bool(
            self.env["account.move"]
            .browse(self.env.context.get("active_ids", []))
            .filtered(lambda x: x.state != "draft")
        )
    )

    def action_change_company(self):
        def _equivalent(model, _id):
            record = self.env[model].browse(_id).sudo()
            result = (
                record.company_id
                and record._company_cascade_get_all(self.company_id).id
                or record.id
            )

            result_record = self.env[model].browse(result).sudo()
            if result_record.company_id and result_record.company_id != self.company_id:
                raise exceptions.UserError(
                    _(
                        "No equivalent record found for %(record)s in company %(company)s"
                    )
                    % {
                        "record": record.display_name,
                        "company": self.company_id.name,
                    }
                )

            return result

        moves = self.env["account.move"].browse(self.env.context.get("active_ids", []))
        for move in moves.filtered(lambda x: x.state == "draft"):
            fiscal_position = move.fiscal_position_id
            journal = move.journal_id
            invoice_lines = move.line_ids.filtered(
                lambda x: x.display_type != "line_note"
            ).with_context(skip_invoice_sync=True, check_move_validity=False)
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
                    "debit",
                    "credit",
                    "tax_repartition_line_id",
                ],
                load="_classic_write",
            )
            invoice_lines.write(
                {
                    "credit": 0,
                    "debit": 0,
                    "amount_currency": False,
                    "balance": 0,
                }
            )
            invoice_lines.env.flush_all()
            invoice_lines.write(
                {
                    "display_type": "line_note",
                    "account_id": False,
                    "tax_ids": False,
                }
            )
            invoice_lines.env.flush_all()
            move.with_context(skip_invoice_sync=True, check_move_validity=False).write(
                {
                    "company_id": self.company_id.id,
                    "fiscal_position_id": fiscal_position.sudo()
                    ._company_cascade_get_all(self.company_id)
                    .id,
                    "journal_id": journal.sudo()
                    ._company_cascade_get_all(self.company_id)
                    .id,
                    "line_ids": [
                        fields.Command.update(
                            vals.pop("id"),
                            dict(
                                vals,
                                company_id=self.company_id.id,
                                account_id=_equivalent(
                                    "account.account", vals["account_id"]
                                ),
                                tax_ids=[
                                    _equivalent("account.tax", tax_id)
                                    for tax_id in vals["tax_ids"]
                                ],
                                analytic_distribution={
                                    str(
                                        _equivalent(
                                            "account.analytic.account", int(_id)
                                        )
                                    ): percentage
                                    for _id, percentage in (
                                        vals["analytic_distribution"] or {}
                                    ).items()
                                },
                                tax_repartition_line_id=_equivalent(
                                    "account.tax.repartition.line",
                                    vals["tax_repartition_line_id"],
                                ),
                            ),
                        )
                        for vals in line_vals
                    ],
                }
            )
            move._check_balanced({"records": move})
            move._check_company()
            move.line_ids._check_company()
