from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    moves = env["account.move"].search([])
    env.add_to_compute(moves._fields["invoice_partner_display_name"], moves)
    env.flush_all()
