# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.addons.payment import reset_payment_provider, setup_provider


def post_init_hook(cr, registry):
    setup_provider(cr, registry, "sumit")


def uninstall_hook(cr, registry):
    reset_payment_provider(cr, registry, "sumit")
