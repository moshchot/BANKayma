# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.mail.controllers import mail


class MailController(mail.MailController):
    @classmethod
    def _redirect_to_record(cls, model, res_id, access_token=None, **kwargs):
        """Add an action_id to the redirect url for invoices"""
        response = super()._redirect_to_record(
            model, res_id, access_token=None, **kwargs
        )
        if (
            model == "account.move"
            and response.status_code == 303
            and "action" not in response.headers.get("location", "action")
        ):
            move = request.env[model].sudo().browse(res_id)
            action = (
                request.env.ref(
                    "bankayma_account.action_bankayma_group_income_move_internal"
                )
                if (
                    move.journal_id.intercompany_sale_company_id
                    or move.journal_id.intercompany_overhead_company_id
                    or move.journal_id.intercompany_purchase_company_id
                )
                else request.env.ref(
                    "bankayma_account.action_bankayma_group_expense_move"
                )
                if (move.move_type in ("in_invoice", "out_refund"))
                else request.env.ref(
                    "bankayma_account.action_bankayma_group_income_move_out_invoice"
                )
            )
            response.headers["location"] += "&action=%s&view_type=form" % action.id
        return response
