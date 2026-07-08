# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib.openupgrade import (
    lift_constraints,
    table_exists,
    update_module_names,
)
from openupgradelib.openupgrade_merge_records import merge_records

from odoo import SUPERUSER_ID, api
from odoo.fields import Command
from odoo.tools import mute_logger

_logger = logging.getLogger("bankayma_migrate_v18")


def pre_init_hook(cr):
    cr.execute(
        """
        --- revert multilanguage for res_partner#{name,city,function,street,street2}
        alter table res_partner add column name_unilanguage varchar;
        update res_partner set name_unilanguage=coalesce(name->>'he_IL', name->>'en_US');
        alter table res_partner rename column name to name_multilanguage;
        alter table res_partner rename column name_unilanguage to name;
        alter table res_partner add column street_unilanguage varchar;
        update res_partner set street_unilanguage=coalesce(street->>'he_IL', street->>'en_US');
        alter table res_partner rename column street to street_multilanguage;
        alter table res_partner rename column street_unilanguage to street;
        alter table res_partner add column street2_unilanguage varchar;
        update res_partner set street2_unilanguage=coalesce(
            street2->>'he_IL', street2->>'en_US'
        );
        alter table res_partner rename column street2 to street2_multilanguage;
        alter table res_partner rename column street2_unilanguage to street2;
        alter table res_partner add column city_unilanguage varchar;
        update res_partner set city_unilanguage=coalesce(city->>'he_IL', city->>'en_US');
        alter table res_partner rename column city to city_multilanguage;
        alter table res_partner rename column city_unilanguage to city;
        alter table res_partner add column function_unilanguage varchar;
        update res_partner set function_unilanguage=coalesce(
            function->>'he_IL', function->>'en_US'
        );
        alter table res_partner rename column function to function_multilanguage;
        alter table res_partner rename column function_unilanguage to function;
        --- revert multilanguage for res_company#name
        alter table res_company add column name_unilanguage varchar;
        update res_company set name_unilanguage=coalesce(name->>'he_IL', name->>'en_US');
        alter table res_company rename column name to name_multilanguage;
        alter table res_company rename column name_unilanguage to name;
        --- set code for all companies
        update res_company set code='code' || id::text where code is null;
        """
    )

    for table in (
        "res_company",
        "res_company_bankayma_website_image_rel",
        "res_company_crew_res_partner_rel",
        "res_company_res_company_tag_rel",
    ):
        if not table_exists(cr, table):
            continue
        # pylint: disable=sql-injection
        cr.execute(f"create table {table}_bk_pre_v18 as select * from {table}")

    for table, column in (
        ("ir_attachment", "res_id"),
        ("event_event", "company_id"),
        ("blog_post", "company_id"),
        ("product_template", "bankayma_website_sale_company_id"),
        ("loyalty_program", "bankayma_website_sale_company_id"),
    ):
        if not table_exists(cr, table):
            continue
        # pylint: disable=sql-injection
        cr.execute(f"alter table {table} add column {column}_bk_pre_v18 int")
        # pylint: disable=sql-injection
        cr.execute(f"update {table} set {column}_bk_pre_v18={column}")


def post_init_hook_assign_records(env, company, ou, extra_models=None):
    for model in ("account.move", "account.move.line") + (
        extra_models and extra_models or ()
    ):
        records = (
            env[model]
            .with_context(active_test=False)
            .search(
                [
                    ("company_id", "=", company.id),
                ]
            )
        )
        validate_fields = records._validate_fields
        records.__class__._validate_fields = lambda self, *args, **kwargs: None
        vals = (
            {
                "operating_unit_id": ou.id,
            }
            if "operating_unit_id" in records._fields
            else {
                "operating_unit_ids": ou.ids,
            }
        )
        records.with_context(
            check_move_validity=False,
            skip_validation_check=True,
            skip_account_move_synchronization=True,
        ).write(vals)
        records.__class__._validate_fields = validate_fields


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {}, su=True)
    main_company = env.ref("base.main_company")
    main_ou = env.ref("operating_unit.main_operating_unit")
    cr.execute("drop index account_move_unique_name")

    main_ou.write(
        {
            "bankayma_from_company_id": env.ref("base.main_company").id,
            "name": main_company.name,
            "code": main_company.code,
        }
    )

    company_id2ou_id = {
        main_company.id: main_ou.id,
    }

    post_init_hook_assign_records(env, main_company, main_ou)

    for company in (
        env["res.company"]
        .with_context(active_test=False)
        .search(
            [
                ("id", "!=", main_company.id),
            ],
        )
    ):
        ou = env["operating.unit"].create(
            {
                "bankayma_from_company_id": company.id,
                "code": company.code,
                "name": company.name,
                "partner_id": company.partner_id.id,
                "active": company.active,
                "parent_id": env["operating.unit"]
                .search([("bankayma_from_company_id", "=", company.parent_id.id)])
                .id,
            }
        )

        company_id2ou_id[company.id] = ou.id

        post_init_hook_assign_records(
            env, company, ou, extra_models=("account.analytic.account",)
        )

    for user in env["res.users"].with_context(active_test=False).search([]):
        user.default_operating_unit_id = user.company_id.bankayma_to_operating_unit_ids
        user.operating_unit_ids = [
            Command.set(user.company_ids.bankayma_to_operating_unit_ids.ids)
        ]

    # break cascading for accounts with own code
    for account in (
        env["account.account"]
        .with_context(active_test=False)
        .search([("company_cascade_child_ids", "!=", False)])
    ):
        if account.company_id.code and account.code.startswith(account.company_id.code):
            account.operating_unit_id = company_id2ou_id[account.company_id.id]
            for child_account in account.company_cascade_child_ids:
                if child_account.company_id.code and child_account.code.startswith(
                    child_account.company_id.code
                ):
                    child_account.operating_unit_id = company_id2ou_id[
                        child_account.company_id.id
                    ]
                    child_account.company_cascade_parent_id = False

    # ir.property values are by stipulation the same for all companies
    lift_constraints(env.cr, "ir_property", "company_cascade_parent_id")
    env.cr.execute(
        f"""
        delete from ir_property
        where company_id <> {main_company.id}
        """
    )

    # eliminate duplicates because otherwise merge_records switches to
    # row mode which is very slow
    m2m_with_duplicates = {
        "account.account": [
            "tag_ids",
        ],
        "account.journal": [
            "bankayma_restrict_product_ids",
        ],
        "account.tax.repartition.line": [
            "tag_ids",
        ],
    }

    for model in (
        "account.account",
        "account.analytic.account",
        "account.analytic.plan",
        "account.fiscal.position",
        "account.fiscal.position.tax",
        "account.fiscal.position.account",
        "account.journal",
        "account.payment.method.line",
        "account.payment.mode",
        "account.payment.term",
        "account.tax",
        "account.tax.repartition.line",
        "ir.sequence",
        "payment.provider",
    ):
        records = (
            env[model]
            .with_context(active_test=False)
            .search(
                [
                    ("company_id", "=", main_company.id),
                    ("company_cascade_child_ids", "!=", False),
                ]
            )
        )
        _logger.info("merging model %s, %d records", model, len(records))
        lift_constraints(env.cr, env[model]._table, "company_cascade_parent_id")
        for record in records:
            other_records = record._company_cascade_get_all() - record
            for field_name in m2m_with_duplicates.get(model, []):
                field = env[model]._fields[field_name]
                env.cr.execute(
                    f"""
                    DELETE from {field.relation}
                    WHERE {field.column1} in {tuple(other_records.ids)}
                    AND {field.column2} IN (
                        SELECT {field.column2} FROM
                        {field.relation}
                        WHERE {field.column1} = {record.id}
                    )
                    """
                )
            with mute_logger("OpenUpgrade"):
                merge_records(
                    env,
                    record._name,
                    other_records.ids,
                    record.id,
                    method="sql",
                )
        env.cr.commit()

    for unique_name_model in ("account.reconcile.model",):
        for record in (
            env[unique_name_model]
            .with_context(active_test=False)
            .search([("company_id", "=", main_company.id)])
        ):
            to_merge = (
                env[unique_name_model]
                .with_context(active_test=False)
                .search(
                    [
                        ("company_id", "!=", main_company.id),
                        ("name", "=", record.name),
                    ]
                )
            )
            if not to_merge:
                continue
            with mute_logger("OpenUpgrade"):
                merge_records(env, record._name, to_merge.ids, record.id, method="sql")

    _logger.info("merging companies")
    with mute_logger("OpenUpgrade"), mute_logger("odoo.sql_db"):
        merge_records(
            env,
            "res.company",
            (
                env["res.company"].with_context(active_test=False).search([])
                - main_company
            ).ids,
            main_company.id,
            method="sql",
        )
    _logger.info("done merging companies")

    multicompany_group = env.ref("base.group_multi_company")
    multi_ou_group = env.ref("operating_unit.group_multi_operating_unit")
    env.ref("base.group_user").implied_ids -= multicompany_group
    env.ref("base.group_user").implied_ids += multi_ou_group
    env["res.users"].with_context(active_test=False).search([]).write(
        {
            "groups_id": [
                Command.unlink(multicompany_group.id),
                Command.link(multi_ou_group.id),
            ],
        }
    )
    update_module_names(
        cr,
        [
            ("company_cascade", "bankayma_base"),
            ("company_cascade_category", "bankayma_base"),
        ],
        merge_modules=True,
    )
