# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "System 1000",
    "summary": "Enables exports to system 1000",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting/Localizations",
    "website": "https://github.com/moshchot/BANKayma",
    "author": "Hunki Enterprises BV, Moshchot Coop, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/l10n_il_system1000_export.xml",
        "views/res_company.xml",
    ],
    "demo": [],
}
