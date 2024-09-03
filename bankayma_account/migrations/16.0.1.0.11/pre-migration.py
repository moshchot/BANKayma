from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Delete views created by this addon for transition to donation dependency
    """
    for xmlid in (
        "view_account_move_form",
        "view_account_move_tree_invoice",
        "view_res_bank_form",
        "view_partner_form",
        "view_partner_property_form_account_fiscal_position_vat_check",
        "view_partner_form_contract",
    ):
        record = env.ref("bankayma_account.%s" % xmlid, False)
        if record:
            record.with_context(_force_unlink=True).unlink()
