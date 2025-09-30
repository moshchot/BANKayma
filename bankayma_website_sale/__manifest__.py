# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (website_sale)",
    "summary": "BANKayma website_sale customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_account",
        "bankayma_website",
        "website_event_sale",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "security/bankayma_website_sale.xml",
        "templates/company_page.xml",
        "templates/website_sale.xml",
        "views/product_template.xml",
    ],
    "demo": [],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {"python": []},
}
