# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Operating Unit Switch",
    "summary": "Switch default OU and filter visible documents from OUs",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Productivity",
    "website": "https://github.com/moshchot/BANKayma",
    "author": "Hunki Enterprises BV, Moshchot Coop, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "preloadable": True,
    "depends": [
        "operating_unit",
    ],
    "assets": {
        "web.assets_backend": [
            "/operating_unit_switcher/static/src/*.js",
            "/operating_unit_switcher/static/src/*.xml",
        ],
        "web.assets_tests": [
            "/operating_unit_switcher/static/tests/tours/*.js",
        ],
    },
}
