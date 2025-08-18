# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib.openupgrade_merge_records import merge_records

from odoo import SUPERUSER_ID, api
from odoo.fields import Command


def pre_init_hook(cr):
    cr.execute(
        """
        --- revert multilanguage for res_partner#{city,street,street2}, unused anyways
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
        --- set code for all companies
        update res_company set code='code' || id::text where code is null;
        """
    )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {}, su=True)
    main_company = env.ref("base.main_company")
    cr.execute("drop index account_move_unique_name")
    for company in (
        env["res.company"]
        .with_context(active_test=False)
        .search(
            [
                ("id", "!=", main_company.id),
            ]
        )
    ):
        ou = env["operating.unit"].create(
            {
                "bankayma_from_company_id": company.id,
                "code": company.code,
                "name": company.name,
                "partner_id": company.partner_id.id,
            }
        )
        for model in ("account.move", "account.move.line"):
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
            records.with_context(skip_validation_check=True).write(
                {
                    "operating_unit_id": ou.id,
                }
            )
            records.__class__._validate_fields = validate_fields

    env.ref("operating_unit.main_operating_unit").bankayma_from_company_id = env.ref(
        "base.main_company"
    )

    for user in env["res.users"].with_context(active_test=False).search([]):
        user.default_operating_unit_id = user.company_id.bankayma_to_operating_unit_ids
        user.operating_unit_ids = [
            Command.set(user.company_ids.bankayma_to_operating_unit_ids.ids)
        ]

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
        "ir.property",
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
        for record in records:
            merge_records(
                env,
                record._name,
                (record._company_cascade_get_all() - record).ids,
                record.id,
                method="sql",
            )
            env.cr.commit()
    # TODO: merge/drop analytic plan columns
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
            merge_records(env, record._name, to_merge.ids, record.id, method="sql")

    merge_records(
        env,
        "res.company",
        (
            env["res.company"].with_context(active_test=False).search([]) - main_company
        ).ids,
        main_company.id,
        method="sql",
    )

    multicompany_group = env.ref("base.group_multi_company")
    env.ref("base.group_user").implied_ids -= multicompany_group
    env["res.users"].with_context(active_test=False).search([]).write(
        {
            "groups_id": [Command.unlink(multicompany_group.id)],
        }
    )
