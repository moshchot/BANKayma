from openupgradelib.openupgrade import copy_columns, migrate


@migrate()
def migrate(env, version=None):
    copy_columns(
        env.cr,
        {
            "account_move": [("validated_state", None, None)],
        },
    )
