from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env["ir.model.data"].search(
        [
            ("module", "=", "base"),
            ("name", "=", "template_portal_user_id"),
        ]
    ).noupdate = True
