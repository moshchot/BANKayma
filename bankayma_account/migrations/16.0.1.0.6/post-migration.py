from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    journals = env["account.journal"].search(
        [
            ("intercompany_purchase_company_id", "!=", False),
        ]
    )
    for journal in journals:
        account = env["account.account"].search(
            [
                ("company_id", "=", journal.company_id.id),
                ("code", "=ilike", "2%11"),
            ],
            limit=1,
        )
        move_lines = env["account.move.line"].search(
            [
                ("journal_id", "=", journal.id),
                ("account_id.code", "=ilike", "2%04"),
            ]
        )
        if move_lines:
            env.cr.execute(
                "update account_move_line set account_id=%s where id in %s",
                (account.id, tuple(move_lines.ids)),
            )
