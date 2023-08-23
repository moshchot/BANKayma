from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env["ir.model.data"].search(
        [
            ("module", "=", "bankayma_account"),
            ("name", "=", "tax_group_vendor_specific"),
        ]
    ).unlink()
