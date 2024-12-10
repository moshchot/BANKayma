# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    comment = fields.Text()
    use_sumit_journal = fields.Boolean()
    use_sumit_this_payment = fields.Boolean(string="Push to sumit")
    other_line_ids = fields.Many2many(
        "account.move.line",
        "account_payment_register_other_line_rel",
    )

    def default_get(self, fields_list):
        # call super only with lines from one company, save others for later
        all_records = self.env[self.env.context["active_model"]].browse(
            self.env.context.get("active_ids", [])
        )
        first_company = all_records[:1].company_id
        self = self.with_context(
            active_ids=all_records.filtered(lambda x: x.company_id == first_company).ids
        )

        result = super().default_get(fields_list)

        other_records = all_records.filtered(lambda x: x.company_id != first_company)
        result["other_line_ids"] = [
            fields.Command.set(
                other_records.ids
                if other_records._name == "account.move.line"
                else other_records.line_ids.ids
            )
        ]

        result["use_sumit_journal"] = (
            self.env["account.move.line"]
            .browse(result.get("line_ids", [(False, False, [])])[0][2])
            .mapped("move_id.journal_id.use_sumit")[0]
        )
        result["use_sumit_this_payment"] = result["use_sumit_journal"]
        return result

    def _create_payments(self):
        """Create invoice from parent company for paid invoices"""
        all_lines = self.line_ids + self.other_line_ids
        last_result = None
        for company in all_lines.company_id:
            self = self.with_company(company).with_context(
                active_ids=all_lines.filtered(lambda x: x.company_id == company).ids,
                active_model="account.move.line",
            )
            defaults = self.default_get(self._fields)
            defaults.pop("other_line_ids", False)
            payment_method = self.payment_method_line_id._company_cascade_get_all(
                company
            )
            defaults.update(
                {
                    "journal_id": self.journal_id._company_cascade_get_all(company),
                    "payment_method_line_id": payment_method,
                    "payment_date": self.payment_date,
                }
            )
            self.write(defaults)
            if self.use_sumit_journal and not self.use_sumit_this_payment:
                for journal in self.line_ids.mapped("move_id.journal_id"):
                    journal.read(["use_sumit"])
                    journal._cache["use_sumit"] = False
            last_result = super()._create_payments()
        return last_result
