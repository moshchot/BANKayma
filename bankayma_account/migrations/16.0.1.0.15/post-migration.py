from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Set analytic tags on tax lines of taxes previously without
    analytic=True; fix vendor specific taxes
    """
    env["account.tax"].with_context(active_test=False).search(
        [
            ("bankayma_vendor_specific", "=", True),
        ]
    ).write({"analytic": True})

    env["account.move.line"].search([("tax_line_id.analytic", "=", True)]).with_context(
        skip_invoice_sync=True
    ).write(
        {
            "analytic_distribution": False,
        }
    )
    for line in env["account.move.line"].search(
        [
            ("tax_ids.analytic", "=", True),
            ("analytic_distribution", "!=", False),
        ]
    ):
        distribution = line.analytic_distribution
        line.with_context(skip_invoice_sync=True).write(
            {
                "analytic_distribution": False,
            }
        )

        wizard = (
            env["account.move.update.analytic.wizard"]
            .with_context(active_id=line.id)
            .create(
                {
                    "analytic_distribution": distribution,
                }
            )
        )

        wizard.update_analytic_lines()
