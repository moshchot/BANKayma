# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (membership)",
    "summary": "BANKayma membership customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_website_sale",
        "membership",
    ],
    "data": [
        "security/bankayma_membership.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/product_template.xml",
    ],
    "demo": [
        "demo/res_users.xml",
    ],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {"python": []},
}
