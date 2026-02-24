# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (website_sale_loyality)",
    "summary": "BANKayma website_sale_loyality customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_website_sale",
        "website_sale_loyalty",
    ],
    "data": [
        "views/loyalty_reward.xml",
        "views/loyalty_program.xml",
    ],
    "demo": [],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {"python": []},
}
