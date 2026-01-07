from openupgradelib import openupgrade

from odoo.fields import Command


@openupgrade.migrate()
def migrate(env, version=None):
    sales_manager_group = env.ref("sales_team.group_sale_manager")

    env.ref("base.default_user").write(
        {"groups_id": [Command.unlink(sales_manager_group.id)]}
    )

    for group in sales_manager_group:
        for user in env["res.users"].search([("groups_id", "=", group.id)]):
            if (
                user.has_group("bankayma_base.group_full")
                or user.has_group("bankayma_base.group_org_manager")
                or user.has_group("base.group_settings")
            ):
                continue
            user.write({"groups_id": [Command.unlink(group.id)]})
