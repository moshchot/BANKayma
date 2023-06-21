# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Spreadsheet in traditional dashboard",
    "summary": "Add spreadsheets to traditional dashboards",
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
        "spreadsheet_dashboard_oca",
        "board",
    ],
    "data": [
        "views/spreadsheet_dashboard.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "spreadsheet_board/static/src/BoardController.esm.js",
            "spreadsheet_board/static/src/BoardController.xml",
            "spreadsheet_board/static/src/SpreadsheetBoard.esm.js",
            "spreadsheet_board/static/src/SpreadsheetBoard.xml",
        ],
    },
}
