from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    partners = env["res.partner"].with_context(active_test=False).search([])
    for partner in partners:
        env.add_to_compute(partners._fields["display_name"], partner)
        env.flush_all()
