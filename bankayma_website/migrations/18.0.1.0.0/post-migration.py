from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    env.cr.execute(
        """
        UPDATE
        operating_unit ou
        SET
        website_description=rc.website_description,
        seo_name=rc.seo_name,
        bankayma_website_subtitle=rc.bankayma_website_subtitle,
        bankayma_inception_year=rc.bankayma_inception_year,
        bankayma_website_opening_hours=rc.bankayma_website_opening_hours,
        bankayma_website_videolink=rc.bankayma_website_videolink,
        social_twitter=rc.social_twitter,
        social_facebook=rc.social_facebook,
        social_instagram=rc.social_instagram,
        social_youtube=rc.social_youtube
        FROM res_company_bk_pre_v18 rc
        WHERE
        rc.id=ou.bankayma_from_company_id
        """
    )
    env.cr.execute(
        """
        UPDATE
        ir_attachment
        SET
        res_model='operating.unit',
        res_id=ou.id
        FROM
        operating_unit ou
        WHERE
        ir_attachment.res_model='res.company'
        AND ir_attachment.res_field='bankayma_website_cover'
        AND ou.bankayma_from_company_id=ir_attachment.res_id_bk_pre_v18
        """
    )
    env.cr.execute(
        """
        INSERT INTO
        operating_unit_bankayma_website_image_rel
        (operating_unit_id, ir_attachment_id)
        SELECT
            ou.id, rel.ir_attachment_id
            FROM
            res_company_bankayma_website_image_rel_bk_pre_v18 rel
            JOIN
            operating_unit ou
            ON
            ou.bankayma_from_company_id=rel.res_company_id
        """
    )
    env.cr.execute(
        """
        INSERT INTO
        operating_unit_crew_res_partner_rel
        (operating_unit_id, res_partner_id)
        SELECT
            ou.id, rel.res_partner_id
            FROM
            res_company_crew_res_partner_rel_bk_pre_v18 rel
            JOIN
            operating_unit ou
            ON
            ou.bankayma_from_company_id=rel.res_company_id
        """
    )
    # delete all website-specific qweb templates as they will be outdated anyways and
    # if there are child views, they'll most likely fail when copied to inherit from
    # the outdated parent templates
    env["ir.ui.view"].sudo().with_context(active_test=False).search(
        [("type", "=", "qweb"), ("website_id", "!=", False)]
    ).unlink()
