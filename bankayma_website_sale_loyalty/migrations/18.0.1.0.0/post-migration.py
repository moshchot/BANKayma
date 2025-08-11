from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    # update program type value
    env.cr.execute(
        """
        UPDATE loyalty_program
        SET bankayma_program_type='promo_code_ou'
        WHERE bankayma_program_type='promo_code_company'
        """
    )
    # set links to OUs
    link_fields = {
        "loyalty.program": "bankayma_website_sale_company_id",
    }
    for model in ("loyalty.program",):
        link_field = link_fields.get(model) or "company_id"
        env.cr.execute(
            f"""
            UPDATE {env[model]._table} model_table
            SET operating_unit_id=ou.id
            FROM
            operating_unit ou
            WHERE
            ou.bankayma_from_company_id=model_table.{link_field}_bk_pre_v18
            """
        )
