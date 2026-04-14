# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Operating Unit Colors",
    "summary": "Set colors for default operating unit",
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
        "operating_unit_switcher",
        "web_company_color",
    ],
    "data": [
        "views/operating_unit.xml",
        "data/ir_attachment.xml",
        "data/ir_asset.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/operating_unit_switcher_color/static/src/*.js",
        ],
    },
}
