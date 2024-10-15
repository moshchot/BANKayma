from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    for company in env["res.company"].search(
        [("parent_id", "!=", False), ("company_cascade_from_parent", "=", True)]
    ):
        company._company_cascade_fix_hierarchy()
