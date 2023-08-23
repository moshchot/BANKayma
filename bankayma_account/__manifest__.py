# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (account)",
    "summary": "BANKayma accounting customizations",
    "version": "16.0.1.0.2",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_analytic_plan_applicability_product",
        "account_due_list",
        "account_due_list_payment_mode",
        "account_financial_report",
        "account_fiscal_position_vat_check",
        "account_template_active",
        "account_mass_reconcile",
        "account_move_name_sequence",
        "account_move_tier_validation",
        "account_move_update_analytic",
        "account_invoice_inter_company",
        "account_invoice_fiscal_position_update",
        "account_payment_partner",
        "account_payment_mode",
        "account_statement_base",
        "account_usability",
        "base_tier_validation_server_action",
        "bankayma_base",
        "company_cascade",
        "currency_rate_update",
        "email_template_qweb",
        "l10n_il",
        "l10n_il_bank",
        "mis_builder",
        "web_ir_actions_act_window_page",
    ],
    "demo": [
        "demo/account_journal.xml",
        "demo/tier_definition.xml",
    ],
    "data": [
        "data/account_payment_method.xml",
        "data/product_product.xml",
        "data/mail_template_views.xml",
        "data/mail_template.xml",
        "data/res_company.xml",
        "data/tier_definition.xml",
        "security/ir.model.access.csv",
        "security/bankayma_account.xml",
        "views/menu.xml",
        "views/account_fiscal_position.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_payment_register.xml",
        "views/dashboard.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "views/templates.xml",
        "wizards/bankayma_company_create.xml",
        "wizards/bankayma_vendor_invite.xml",
        "wizards/mass_editing_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bankayma_account/static/src/*.xml",
        ],
        "web.assets_common": [
            (
                "replace",
                "web/static/lib/select2/select2.js",
                "bankayma_account/static/lib/select2.full.min.js",
            ),
        ],
        "web.assets_frontend": [
            # TODO make this website_select2_bootstrap in oca/website eventually
            (
                "replace",
                "web/static/lib/select2/select2.js",
                "bankayma_account/static/lib/select2.full.min.js",
            ),
            (
                "replace",
                "web/static/lib/select2/select2.css",
                "bankayma_account/static/lib/select2.min.css",
            ),
            (
                "replace",
                "web/static/lib/select2-bootstrap-css/select2-bootstrap.css",
                "bankayma_account/static/lib/select2-bootstrap-5-theme.min.css",
            ),
            "bankayma_account/static/src/select2-bootstrap.js",
        ],
    },
    "website": "https://github.com/moshchot/BANKayma",
}
