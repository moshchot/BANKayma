# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (website)",
    "summary": "BANKayma website customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_account",
        "website",
        "website_event",
        "partner_multi_relation",
        "res_company_category",
    ],
    "data": [
        "data/res_partner_relation_type.xml",
        "views/templates.xml",
        "views/res_company.xml",
        "views/res_company_category.xml",
    ],
    "demo": [],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {"python": []},
}
