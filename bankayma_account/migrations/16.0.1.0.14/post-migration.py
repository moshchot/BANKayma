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

    for line in env["account.move.line"].search(
        [
            ("tax_ids.analytic", "=", True),
            ("analytic_distribution", "!=", False),
        ]
    ):
        line.move_id.line_ids.filtered(
            lambda x: x.tax_line_id.analytic and x.tax_line_id in line.tax_ids
        ).with_context(skip_invoice_sync=True).write(
            {
                "analytic_distribution": line.analytic_distribution,
            }
        )
        wizard = (
            env["account.move.update.analytic.wizard"]
            .with_context(active_id=line.id)
            .create({})
        )

        wizard.update_analytic_lines()
