# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    post_to_chatter = fields.Boolean()

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        email_layout_xmlid=False,
    ):
        if self.post_to_chatter:
            record = self.env[self.model].browse(res_id or [])
            values = self.generate_email(res_id, ["body_html"])
            record.message_post(
                body=values["body_html"],
                message_type="comment",
                subtype_id=self.env.ref("bankayma_base.message_subtype_internal").id,
            )
        mail_id = super().send_mail(
            res_id,
            force_send=force_send,
            raise_exception=raise_exception,
            email_values=email_values,
            email_layout_xmlid=email_layout_xmlid,
        )
        mail = self.env["mail.mail"].browse(mail_id)
        if not mail.recipient_ids and not mail.email_to and not mail.email_cc:
            mail.unlink()
            mail_id = False
        return mail_id
