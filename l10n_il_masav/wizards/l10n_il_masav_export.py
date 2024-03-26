# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io
from base64 import b64encode

from masav import MasavPayingInstitute, MasavPaymentDetails

from odoo import _, api, exceptions, fields, models


class L10nIlMasavExport(models.TransientModel):
    _name = "l10n.il.masav.export"
    _description = "Masav export"

    export_file = fields.Binary(readonly=True)
    export_file_name = fields.Char(readonly=True)
    payment_date = fields.Date(
        default=lambda self: fields.Date.context_today(self), required=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        compute="_compute_state",
    )

    @api.depends("export_file")
    def _compute_state(self):
        for this in self:
            if not this.export_file:
                this.state = "draft"
            else:
                this.state = "done"

    def button_export(self):
        moves = self.env["account.move"].browse(self.env.context.get("active_ids", []))
        company = moves.mapped("company_id")

        if len(company) > 1:
            raise exceptions.UserError(
                _("You can only export moves of the same company")
            )

        masav_id = "".join(filter(str.isnumeric, company.l10n_il_masav_id or ""))
        vat = "".join(filter(str.isnumeric, company.vat or ""))

        if not masav_id:
            raise exceptions.UserError(
                _("Company %s is missing its MASAV id") % company.name
            )

        if not vat:
            raise exceptions.UserError(
                _("Company %s is missing its VAT") % company.name
            )

        if set(moves.mapped("move_type")) != {"in_invoice"}:
            raise exceptions.UserError(_("You can only export vendor bills"))

        if set(moves.mapped("state")) != {"posted"}:
            raise exceptions.UserError(_("You can only export posted bills"))

        institute = MasavPayingInstitute(
            institute_code=masav_id,
            institute_name=company.name,
            sending_institute_code=vat[:-5],
        )

        transactions = []

        for move in moves:
            partner = move.partner_id
            bank_account = partner.bank_ids[:1]
            bank = bank_account.bank_id
            branch_code = bank_account.branch_code or bank.bank_branch_code

            if not all((branch_code, bank.bank_code, bank_account.acc_number)):
                raise exceptions.UserError(
                    _(
                        "Partner %s is missing bank account information "
                        "(bank code, branch code, account number)"
                    )
                    % partner.name
                )

            if not partner.vat:
                raise exceptions.UserError(
                    _("Partner %s is missing vat") % partner.name
                )

            transactions.append(
                MasavPaymentDetails(
                    amount=move.amount_total,
                    bank_number=bank.bank_code,
                    branch_number=branch_code,
                    account_number=bank_account.acc_number,
                    payee_id="".join(filter(str.isnumeric, partner.vat)),
                    payee_name=partner.name,
                    payee_number=move.id,
                )
            )

        serial = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "l10n_il_masav.sequence_number",
                "1",
            )
        )

        buffer = io.BytesIO()

        def _save_content_to_buffer(file, file_content):
            buffer.writelines(file_content)

        institute._save_content_to_file = _save_content_to_buffer

        institute.create_payment_file(
            file="",
            payments_list=transactions,
            payment_date=self.payment_date.strftime("%y%m%d"),
            serial_number=serial,
            creation_date=fields.Date.today().strftime("%y%m%d"),
        )

        self.env["ir.config_parameter"].sudo().set_param(
            "l10n_il_masav.sequence_number",
            str(serial + 1),
        )

        self.export_file = b64encode(buffer.getbuffer())
        self.export_file_name = "%s-%s.msv" % (
            masav_id,
            fields.Date.today().strftime("%Y%m%d"),
        )
        action_dict = self.env["ir.actions.actions"]._for_xml_id(
            "l10n_il_masav.action_l10n_il_masav_export"
        )
        action_dict.update(res_id=self.id)
        return action_dict
