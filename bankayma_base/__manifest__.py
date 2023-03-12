# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma",
    "summary": "BANKayma base module",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "base_technical_features",
        "module_auto_update",
        "res_company_code",
        "web_select_all_companies",
    ],
    "data": [
        "security/bankayma_base.xml",
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
}
