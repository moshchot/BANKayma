# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree
from markupsafe import Markup

from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    post_to_chatter = fields.Boolean(
        help="Post mails sent by this template to chatter. "
        "This is necessary to receive replies to mail generated from the template"
    )

    def send_mail_batch(
        self,
        res_ids,
        force_send=False,
        raise_exception=False,
        email_values=None,
        email_layout_xmlid=False,
    ):
        """
        Implement chatter-like behavior for email templates
        """
        records2email_values = {}
        records = self.env[self.model].browse(res_ids or [])

        if self.post_to_chatter:
            for record in records:
                values = self._generate_template(record.ids, ["body_html"])[record.id]

                body_doc = etree.fromstring(values["body_html"], etree.HTMLParser())
                for element in body_doc.xpath("//div[@id='header' or @id='footer']"):
                    element.getparent().remove(element)

                message = record.message_post(
                    body=Markup(etree.tostring(body_doc).decode("utf8")),
                    message_type="comment",
                    subtype_id=self.env.ref(
                        "bankayma_base.message_subtype_internal"
                    ).id,
                )

                records2email_values[record] = dict(
                    email_values or {}, message_id=message.message_id
                )
        else:
            records2email_values[records] = email_values

        mails = self.env["mail.mail"]

        for records, email_values in records2email_values.items():
            mails += super().send_mail_batch(
                records.ids,
                force_send=force_send,
                raise_exception=raise_exception,
                email_values=email_values,
                email_layout_xmlid=email_layout_xmlid,
            )

        for mail in mails.exists():
            if not mail.recipient_ids and not mail.email_to and not mail.email_cc:
                mail.unlink()

        return mails.exists() or self.new({})
