from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Migrate all intercompany moves from templates (=companies with root
    company as parent) to root company
    """
    root_company = env.ref("base.main_company")
    template_companies = env["res.company"].search(
        [("parent_id", "=", root_company.id)]
    )
    for move in env["account.move"].search(
        [("company_id", "in", template_companies.ids)]
    ):
        env.cr.execute(
            """
            update account_move set
            company_id=%(company_id)s,
            journal_id=%(journal_id)s
            where id=%(move_id)s
            """,
            {
                "move_id": move.id,
                "company_id": root_company.id,
                "journal_id": move.journal_id._company_cascade_get_all(root_company).id,
            },
        )
        for move_line in move.line_ids:
            env.cr.execute(
                """
                update account_move_line set
                company_id=%(company_id)s,
                journal_id=%(journal_id)s,
                account_id=%(account_id)s,
                group_tax_id=%(group_tax_id)s,
                tax_line_id=%(tax_line_id)s
                where id=%(move_line_id)s
                """,
                {
                    "move_line_id": move_line.id,
                    "company_id": root_company.id,
                    "journal_id": move.journal_id._company_cascade_get_all(
                        root_company
                    ).id,
                    "account_id": move_line.account_id._company_cascade_get_all(
                        root_company
                    ).id,
                    "group_tax_id": move_line.group_tax_id._company_cascade_get_all(
                        root_company
                    ).id
                    or None,
                    "tax_line_id": move_line.tax_line_id._company_cascade_get_all(
                        root_company
                    ).id
                    or None,
                },
            )
            for tax in move_line.tax_ids:
                env.cr.execute(
                    """
                    update account_move_line_account_tax_rel
                    set account_tax_id=%(tax_id)s
                    where account_move_line_id=%(move_line_id)s
                    """,
                    {
                        "tax_id": tax._company_cascade_get_all(root_company).id,
                        "move_line_id": move_line.id,
                    },
                )
