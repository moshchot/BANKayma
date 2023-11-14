# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class BankaymaVendorInvite(models.TransientModel):
    _inherit = "mail.compose.message"
    _name = "bankayma.vendor.invite"

    attachment_ids = fields.Many2many(
        relation="bankayma_vendor_invite_ir_attachment_rel"
    )
    partner_ids = fields.Many2many(relation="bankayma_vendor_invite_res_partner_rel")

    def default_get(self, fields):
        if (
            self.env["res.partner"]
            .sudo()
            .browse(self.env.context.get("active_ids", []))
            .mapped("user_ids")
        ):
            raise UserError(_("This partner already has a user!"))
        return super().default_get(fields)

    def _action_send_mail(self, auto_commit=False):
        partners = (
            self.env["res.partner"]
            .sudo()
            .browse(self.env.context.get("active_ids", []))
        )
        partners.signup_prepare()
        partners.write(
            {
                "signup_group_ids": [
                    (6, 0, self.env.ref("bankayma_base.group_vendor").ids)
                ],
                "signup_company_ids": [
                    (6, 0, self.env.company.ids),
                ],
            }
        )
        return super()._action_send_mail(auto_commit=auto_commit)
