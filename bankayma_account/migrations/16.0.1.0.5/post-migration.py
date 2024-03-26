from openupgradelib.openupgrade import get_legacy_name, map_values, migrate


@migrate()
def migrate(env, version=None):
    map_values(
        env.cr,
        get_legacy_name("validated_state"),
        "validated_state",
        [
            ("draft", "0_draft"),
            ("needs_validation", "1_needs_validation"),
            ("validated", "2_validated"),
            ("rejected", "3_rejected"),
            ("paid", "4_paid"),
        ],
        table="account_move",
    )
