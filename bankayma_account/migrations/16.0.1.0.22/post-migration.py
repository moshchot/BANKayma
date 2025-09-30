from openupgradelib import openupgrade
from openupgradelib.openupgrade_merge_records import merge_records

from odoo.tools.translate import code_translations


@openupgrade.migrate()
def migrate(env, version=None):
    deduction_tax_groups = (
        env["account.fiscal.position"].search([]).bankayma_deduct_tax_group_id
    )
    if not deduction_tax_groups:
        return
    # merge duplicate taxes
    env.cr.execute(
        """
        select array_agg(id) from account_tax
        where tax_group_id in %s
        group by company_id, amount
        having count(id) > 1
        """,
        (tuple(deduction_tax_groups.ids),),
    )
    no_cascade_env = env(
        context=dict(env.context, company_cascade_up=False, company_cascade=False)
    )
    AccountTax = env["account.tax"]
    for (duplicate_taxes_ids,) in env.cr.fetchall():
        taxes = AccountTax.browse(duplicate_taxes_ids)
        target = taxes.filtered("active")[:1] or taxes[:1]
        merge_records(
            no_cascade_env,
            "account.tax",
            (taxes - target).ids,
            target.id,
            method="sql",
        )
        target.invalidate_cache()
        for field in ("invoice_repartition_line_ids", "refund_repartition_line_ids"):
            for repartition_type in set(target[field].mapped("repartition_type")):
                repartition_lines = target[field].filtered(
                    lambda x: x.repartition_type == repartition_type
                )
                if len(repartition_lines) > 1:
                    merge_records(
                        no_cascade_env,
                        repartition_lines._name,
                        repartition_lines[1:].ids,
                        repartition_lines[0].id,
                        method="sql",
                    )

    # fix dangling repartition lines
    for repartition_line in no_cascade_env["account.tax.repartition.line"].search(
        [
            ("company_id.parent_id", "!=", False),
            ("company_cascade_parent_id", "=", False),
            "|",
            ("invoice_tax_id.company_cascade_parent_id", "!=", False),
            ("refund_tax_id.company_cascade_parent_id", "!=", False),
        ]
    ):
        repartition_line.company_cascade_parent_id = (
            repartition_line._company_cascade_find_candidate(
                repartition_line.company_id.parent_id,
                repartition_line._company_cascade_values(
                    repartition_line.company_id.parent_id,
                    repartition_line.read([], load="_classic_write")[0],
                ),
            )
        )

    # ensure translated names
    languages = env["res.lang"].search([]).mapped("code")
    for tax in env["account.tax"].search(
        [("tax_group_id", "in", deduction_tax_groups.ids)]
    ):
        for lang in languages:
            tax.with_context(lang=lang).write(
                {
                    "name": code_translations.get_python_translations(
                        "bankayma_account", lang
                    ).get("%(name)s %(percentage)d%%", "%(name)s %(percentage)d%%")
                    % {
                        "name": tax.tax_group_id.with_context(lang=lang).name,
                        "percentage": tax.amount,
                    }
                }
            )
