from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    for page in env["website.page"].search([("name", "=", False)]):
        page.name = page.view_id.name
