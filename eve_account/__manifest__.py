# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "EVE (account)",
    "summary": "EVE accounting customizations",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_account",
        "eve_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_payment_term.xml",
        "views/res_partner.xml",
        "views/menu.xml",
        "wizards/bankayma_company_create.xml",
    ],
    "demo": [],
    "website": "https://github.com/moshchot/BANKayma",
}
