from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # enable sumit provider as it's disabled by neutralization
    provider = env.ref("l10n_il_sumit.payment_provider_sumit")
    provider.write({"state": "enabled"})
    method = env.ref("payment.payment_method_card")
    method.write({"active": True})
