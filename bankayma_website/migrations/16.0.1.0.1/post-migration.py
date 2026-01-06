from openupgradelib import openupgrade

from odoo.fields import Command


@openupgrade.migrate()
def migrate(env, version=None):
    event_manager_group = env.ref("event.group_event_manager")
    mail_template_editor_group = env.ref("mail.group_mail_template_editor")

    env.ref("bankayma_website.group_website").write(
        {
            "implied_ids": [Command.unlink(event_manager_group.id)],
        }
    )
    env.ref("base.group_user").write(
        {
            "implied_ids": [Command.unlink(mail_template_editor_group.id)],
        }
    )
    env.ref("base.default_user").write(
        {"groups_id": [Command.unlink(event_manager_group.id)]}
    )

    for group in event_manager_group + mail_template_editor_group:
        for user in env["res.users"].search([("groups_id", "=", group.id)]):
            if user.has_group("bankayma_base.group_full") or user.has_group(
                "bankayma_base.group_org_manager"
            ):
                continue
            user.write({"groups_id": [Command.unlink(group.id)]})
