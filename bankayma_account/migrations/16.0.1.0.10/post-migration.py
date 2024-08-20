from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Delete retired mail templates to avoid confusion
    """
    for xmlid in (
        "template_account_move_paid",
        "template_account_move_new_from_portal",
        "template_account_move_tier_rejected",
    ):
        env.ref("bankayma_account.%s" % xmlid).unlink()
