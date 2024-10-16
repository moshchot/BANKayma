# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Cascading companies (company category support)",
    "summary": "Sync configuration from parent companies to children",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Technical",
    "website": "https://github.com/moshchot/BANKayma",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA), Moshchot Coop",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": ["company_cascade", "res_company_category"],
    "data": [
        "wizards/company_cascade_wizard.xml",
    ],
}
