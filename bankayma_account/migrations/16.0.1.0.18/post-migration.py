from openupgradelib import openupgrade

from odoo.fields import Command


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Add mail.mt_comment to followers who only have mail_subtype_vendor
    """
    mt_comment = env.ref("mail.mt_comment")
    mt_vendor = env.ref("bankayma_account.message_subtype_vendor")
    followers = env["mail.followers"].search([("subtype_ids", "=", mt_vendor.id)])
    followers.write(
        {
            "subtype_ids": [Command.link(mt_comment.id)],
        }
    )
