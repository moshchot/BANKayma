import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__file__)


@openupgrade.migrate()
def migrate(env, version=None):
    """
    Fix deleted tax lines from 16.0.1.0.15 migration
    """
    env["account.move.line"].__class__._check_reconciliation = lambda self: None
    count = 0
    for invoice in (
        env["account.move"].search([]).with_context(check_move_validity=False)
    ):
        if not invoice._get_unbalanced_moves(dict(records=invoice)):
            continue
        logger.info("working on %s [%s]", invoice.name, invoice.id)
        invoice._cache["state"] = "draft"
        invoice.invoice_line_ids.read(["parent_state"])
        for line in invoice.invoice_line_ids:
            for key, vals in (line.compute_all_tax or {}).items():
                create_vals = {**key, **vals, "display_type": "tax"}
                if "move_id" not in create_vals:
                    continue
                line.create(create_vals)
        if invoice._get_unbalanced_moves(dict(records=invoice)):
            logger.info("could not fix %s", invoice.name)
            break
        else:
            count += 1
    logger.info("fixed %s records", count)
