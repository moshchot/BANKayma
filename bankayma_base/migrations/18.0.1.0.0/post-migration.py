import json

from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # set links to OUs
    link_fields = {
        "product.template": "bankayma_website_sale_company_id",
    }
    for model in ("blog.post", "event.event", "product.template"):
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
    # set OU tags from company tags
    env.cr.execute(
        """
        INSERT INTO
        operating_unit_operating_unit_tag_rel
        (operating_unit_id, operating_unit_tag_id)
        SELECT
            ou.id, rel.res_company_tag_id
            FROM
            res_company_res_company_tag_rel_bk_pre_v18 rel
            JOIN
            operating_unit ou
            ON
            ou.bankayma_from_company_id=rel.res_company_id
        """
    )
    # restore OU colors from company colors
    color_fields = (
        "color_navbar_bg",
        "color_navbar_bg_hover",
        "color_navbar_text",
        "color_button_bg",
        "color_button_bg_hover",
        "color_button_text",
        "color_link_text",
        "color_link_text_hover",
    )
    env.cr.execute(
        """
        SELECT
        ou.id, res_company_legacy.company_colors
        FROM
        res_company_bk_pre_v18 res_company_legacy
        JOIN
        operating_unit ou
        ON
        ou.bankayma_from_company_id=res_company_legacy.id
        """
    )
    OU = env["operating.unit"]
    for ou_id, company_colors in env.cr.fetchall():
        company_colors = json.loads(company_colors or "{}") or {}
        OU.browse(ou_id).write(
            {field_name: company_colors.get(field_name) for field_name in color_fields}
        )
    # restore OU multilang names
    env.cr.execute(
        """
        update operating_unit
        set name=res_company.name_multilanguage
        from res_company_bk_pre_v18 res_company
        where bankayma_from_company_id=res_company.id
        """
    )
