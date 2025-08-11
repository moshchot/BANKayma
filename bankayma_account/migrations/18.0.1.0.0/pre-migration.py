from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # migrate account.move#bankayma_intercompany_grouping
    env.cr.execute(
        """
        ALTER TABLE account_move
        ALTER COLUMN bankayma_intercompany_grouping
        TYPE jsonb
        USING json_build_object(0, bankayma_intercompany_grouping)
        """
    )
