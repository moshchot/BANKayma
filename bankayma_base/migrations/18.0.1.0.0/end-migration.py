from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # uninstall obsolete modules
    env["ir.module.module"].search(
        [
            (
                "name",
                "in",
                [
                    "account_invoice_inter_company",
                ],
            ),
        ]
    ).button_uninstall()
