# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Israeli Banks",
    "summary": "Adds IL specific fields on banks and populates the list of banks",
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
        "partner_bank_code",
    ],
    "data": [
        "data/res_bank.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
