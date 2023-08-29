from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env.cr.execute(
        "select id, bankayma_tax_id, bankayma_tax_id_optional "
        "from account_fiscal_position where bankayma_tax_id is not null"
    )
    for fpos_id, tax_id, optional in env.cr.fetchall():
        env["account.fiscal.position"].browse(fpos_id).write(
            {
                "optional_tax_ids": [(4, tax_id)],
            }
            if optional
            else {
                "bankayma_tax_ids": [(4, tax_id)],
            }
        )
