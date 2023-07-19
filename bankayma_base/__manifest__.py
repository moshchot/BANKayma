# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma",
    "summary": "BANKayma base module",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "attachment_indexation",
        "base_user_effective_permissions",
        "board",
        "barcodes_gs1_nomenclature",
        "contacts",
        "document_knowledge",
        "document_page_approval",
        "mail",
        "disable_odoo_online",
        "base_portal_type",
        "base_technical_features",
        "module_auto_update",
        "portal_odoo_debranding",
        "remove_odoo_enterprise",
        "res_company_code",
        "web_company_color",
        "web_responsive",
        "web_select_all_companies",
        "spreadsheet_dashboard_oca",
        "spreadsheet_board",
        "hr",
        "hr_contract",
        "hr_hourly_cost",
        "hr_org_chart",
        "partner_contact_access_link",
        "partner_contact_lang",
        "portal_rating",
        "project",
        "project_department",
        "project_parent_task_filter",
        "project_role",
        "project_sms",
        "project_task_add_very_high",
        "project_task_default_stage",
        "project_task_personal_stage_auto_fold",
        "project_template",
        "project_timeline",
        "project_type",
        "server_action_mass_edit",
        "social_media",
        "web_advanced_search",
        "web_chatter_position",
        "web_dark_mode",
        "website_blog",
        "website_form_project",
        "website_mail",
        "website_partner",
        "website_payment",
        "web_theme_classic",
        "web_timeline",
        "web_tree_many2one_clickable",
    ],
    "data": [
        "security/bankayma_base.xml",
        "security/ir.model.access.csv",
        "views/res_company.xml",
        "views/res_users.xml",
        "views/templates.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_users.xml",
    ],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {
        "python": [
            "openupgradelib",
            "odoo_test_helper",
        ]
    },
    "assets": {
        "web.assets_backend": [
            "bankayma_base/static/src/css/*backend.css",
            "bankayma_base/static/src/js/BoardController.esm.js",
            "bankayma_base/static/src/xml/BoardController.xml",
        ],
        "web.assets_frontend": [
            "bankayma_base/static/src/css/*frontend.css",
        ],
    },
}
