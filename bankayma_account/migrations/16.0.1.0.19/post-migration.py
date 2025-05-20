from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Recalculate analytic lines of tax lines with editable taxes.
    Analytic lines were not updated when analytic distribution was changed on posted
    moves with manually edited taxes.
    """
    lines = env["account.move.line"].search(
        [
            ("tax_line_id.tax_group_id.bankayma_editable", "=", True),
            ("analytic_line_ids", "!=", False),
        ]
    )
    lines.analytic_line_ids.unlink()
    lines._create_analytic_lines()
