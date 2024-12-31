from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    vendor_subtype = env.ref("bankayma_account.message_subtype_vendor")
    for move in env["account.move"].search([]):
        move.message_subscribe(move.partner_id.ids, vendor_subtype.ids)
