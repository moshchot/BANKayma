# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    comment = fields.Text()
    use_sumit_journal = fields.Boolean()
    use_sumit_this_payment = fields.Boolean(string="Push to sumit")

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        result["use_sumit_journal"] = (
            self.env["account.move.line"]
            .browse(result.get("line_ids", [(False, False, [])])[0][2])
            .mapped("move_id.journal_id.use_sumit")[0]
        )
        result["use_sumit_this_payment"] = result["use_sumit_journal"]
        return result

    def _create_payments(self):
        """Create invoice from parent company for paid invoices"""
        if self.env.user.has_group("bankayma_base.group_org_manager"):
            self = self.with_company(self.mapped("company_id"))
        if self.use_sumit_journal and not self.use_sumit_this_payment:
            for journal in self.line_ids.mapped("move_id.journal_id"):
                journal.read(["use_sumit"])
                journal._cache["use_sumit"] = False
        return super()._create_payments()
