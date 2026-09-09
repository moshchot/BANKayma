from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.copy_columns(
        env.cr,
        {"event_event": [("registration_multi_qty", "registration_single_name", None)]},
    )
    openupgrade.copy_columns(
        env.cr,
        {"event_type": [("registration_multi_qty", "registration_single_name", None)]},
    )
    EventRegistration = env["event.registration"]
    env.cr.execute("SELECT id, qty FROM event_registration WHERE qty > 1")
    for registration_id, qty in env.cr.fetchall():
        registration = EventRegistration.browse(registration_id)
        for _i in range(qty - 1):
            registration.copy(
                {
                    "sale_order_id": registration.sale_order_id.id,
                    "sale_order_line_id": registration.sale_order_line_id.id,
                }
            )
    env["ir.module.module"].search(
        [
            (
                "name",
                "in",
                (
                    "event_registration_multi_qty",
                    "event_sale_registration_multi_qty",
                    "website_event_sale_registration_multi_qty",
                ),
            )
        ]
    ).button_uninstall()
