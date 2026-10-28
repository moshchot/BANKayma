from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env["res.company"].search([]).write(
        {
            "inter_ou_product_id": env["product.product"]
            .search([("default_code", "=", 10)], limit=1)
            .id,
            "inter_ou_journal_id": env["account.journal"]
            .search(
                [
                    ("type", "=", "misc"),
                ],
                limit=1,
            )
            .id,
        }
    )
