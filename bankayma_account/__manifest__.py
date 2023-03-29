# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (account)",
    "summary": "BANKayma accounting customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_due_list",
        "account_fiscal_position_vat_check",
        "account_template_active",
        "account_move_tier_validation",
        "account_invoice_inter_company",
        "account_payment_partner",
        "account_payment_mode",
        "account_usability",
        "bankayma_base",
        "l10n_il",
    ],
    "demo": [
        "demo/tier_definition.xml",
    ],
    "data": [
        "data/account_payment_method.xml",
        "data/ir_cron.xml",
        "data/res_company.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/account_move.xml",
        "views/account_payment_register.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "views/templates.xml",
        "wizards/bankayma_company_create.xml",
        "wizards/company_cascade_wizard.xml",
    ],
    "website": "https://github.com/moshchot/BANKayma",
}
