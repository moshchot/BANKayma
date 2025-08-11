from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env.cr.execute(
        """
        UPDATE
        event_event ee
        SET
        operating_unit_id=ou.id
        FROM
        operating_unit ou
        WHERE
        ou.bankayma_from_company_id=ee.company_id_bk_pre_v18
        """
    )
    env.cr.execute(
        """
        UPDATE
        product_template pp
        SET
        operating_unit_id=ou.id
        FROM
        operating_unit ou
        WHERE
        ou.bankayma_from_company_id=pp.bankayma_website_sale_company_id_bk_pre_v18
        """
    )
