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
        skip_invoice_sync=True,
        dynamic_unlink=True,
        force_delete=True,
        check_move_validity=False,
    ).unlink()
    env["account.move.line"].__class__._check_reconciliation = lambda self: None
    for line in env["account.move.line"].search(
        [
            ("tax_ids.analytic", "=", True),
            ("analytic_distribution", "!=", False),
        ]
    ):
        distribution = line.analytic_distribution
        for move_line in line.move_id.line_ids:
            move_line._cache["parent_state"] = "draft"
        line.write(
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
