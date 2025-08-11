from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # enable sumit provider as it's disabled by neutralization
    provider = env.ref("l10n_il_sumit.payment_provider_sumit")
    provider.write({"state": "enabled"})
    method = env.ref("payment.payment_method_card")
    method.write({"active": True})
    # configure inter OU company fields
    env["res.company"].search([]).write(
        {
            "inter_ou_product_id": env["product.product"]
            .search([("default_code", "=", 10)], limit=1)
            .id,
            "inter_ou_journal_id": env["account.journal"]
            .create(
                {
                    "name": "Inter OU +|-",
                    "type": "general",
                    "code": "IOPP",
                }
            )
            .id,
        }
    )
