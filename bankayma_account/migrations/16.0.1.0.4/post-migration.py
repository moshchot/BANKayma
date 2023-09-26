from openupgradelib.openupgrade import migrate

from odoo.addons.l10n_il_sumit.hooks import post_init_hook


@migrate()
def migrate(env, version=None):
    post_init_hook(env.cr, env.registry)
