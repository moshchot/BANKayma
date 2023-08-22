from openupgradelib.openupgrade import load_data, migrate


@migrate()
def migrate(env, version=None):
    load_data(env.cr, "bankayma_account", "data/mail_template.xml")
