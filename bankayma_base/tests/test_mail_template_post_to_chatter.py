from odoo.tests.common import TransactionCase


class TestMailTemplatePostToChatter(TransactionCase):
    def setUp(self):
        super().setUp()
        self.mail_template = self.env.ref("bankayma_base.template_post_to_chatter")
        self.partner = self.env.ref("base.main_partner")
        self.existing_mails = self.partner.message_ids

    def test_post_to_chatter(self):
        self.mail_template.send_mail(self.partner.id)
        new_mails = self.partner.message_ids - self.existing_mails
        self.assertEqual(len(new_mails), 2)
        self.assertEqual(
            new_mails[0].message_id,
            new_mails[1].message_id,
        )
        internal_mail = new_mails.filtered(
            lambda x: (
                x.subtype_id == self.env.ref("bankayma_base.message_subtype_internal")
            )
        )
        external_mail = new_mails.filtered(lambda x: not x.subtype_id)
        self.assertTrue(internal_mail)
        self.assertTrue(external_mail)

    def test_post_to_chatter_disabled(self):
        self.mail_template.post_to_chatter = False
        self.mail_template.send_mail(self.partner.id)
        new_mails = self.partner.message_ids - self.existing_mails
        self.assertEqual(len(new_mails), 1)
        self.assertFalse(new_mails.subtype_id)
