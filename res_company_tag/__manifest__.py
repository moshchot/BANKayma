# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Tags for companies",
    "summary": "Add tagging functionality for companies",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Productivity",
    "website": "https://github.com/moshchot/BANKayma",
    "author": "Hunki Enterprises BV, Moshchot Coop, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "res_company_search_view",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company.xml",
        "views/res_company_tag.xml",
    ],
    "demo": [
        "demo/res_company_tag.xml",
    ],
}
