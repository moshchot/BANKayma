from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version=None):
    # enable sumit provider as it's disabled by neutralization
    provider = env.ref("l10n_il_sumit.payment_provider_sumit")
    provider.write({"state": "enabled"})
    method = env.ref("payment.payment_method_card")
    method.write({"active": True})
    # configure inter OU company fields
    inter_ou_journal = env["account.journal"].create(
        {
            "name": "Inter OU +|-",
            "type": "general",
            "code": "IOPP",
        }
    )
    env["res.company"].search([]).write(
        {
            "inter_ou_product_id": env["product.product"]
            .search([("default_code", "=", 10)], limit=1)
            .id,
            "inter_ou_journal_id": inter_ou_journal.id,
        }
    )
    # allow journal on all accounts that were previously restricted to interco journals
    env["account.account"].search(
        [
            (
                "allowed_journal_ids",
                "in",
                (
                    env["res.company"].search([]).intercompany_sale_journal_id
                    + env["res.company"].search([]).intercompany_purchase_journal_id
                ).ids,
            ),
        ]
    ).allowed_journal_ids += inter_ou_journal
    # set overhead percentage
    env.cr.execute(
        """
        UPDATE operating_unit
        SET bankayma_overhead_percentage=max_percentage.percentage
        FROM (
            SELECT MAX(bankayma_overhead_percentage) as percentage FROM account_journal
        ) max_percentage
        """
    )
    # deactivate unused standard taxes
    env.cr.execute(
        """
        UPDATE account_tax
        SET active=False
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE model='account.tax' AND module='account' AND name NOT IN (
                '1_il_vat_sales_exempt',
                '1_il_vat_inputs_17',
                '1_il_vat_inputs_2_3_17',
                '1_il_vat_purchase_exempt'
            )
        )
        """
    )
    # write body_html of email_template_edi_invoice because it's noupdate
    # data and we can't force load it because we don't have translations
    # for the field (was a view before which only has translation fragments)
    env.cr.execute(
        """
        UPDATE mail_template
        SET body_html=(
            SELECT arch_db FROM ir_ui_view
            WHERE id IN (
                SELECT res_id FROM ir_model_data
                WHERE module='bankayma_account' AND name='qweb_template_edi_invoice'
            )
        )
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module='account' AND name='email_template_edi_invoice'
        )
        """
    )
