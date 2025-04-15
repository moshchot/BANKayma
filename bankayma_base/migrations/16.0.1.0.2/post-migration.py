from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env["res.partner"].search([("type", "=", "other")]).write({"type": "contact"})
