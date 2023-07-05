# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma",
    "summary": "BANKayma base module",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "board",
        "contacts",
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
    ],
    "data": [
        "security/bankayma_base.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/res_users.xml",
        "views/templates.xml",
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
