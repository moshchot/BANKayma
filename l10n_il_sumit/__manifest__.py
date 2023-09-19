# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sumit",
    "summary": "Support for the Sumit accounting suit",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/moshchot/BANKayma",
    "author": "Hunki Enterprises BV, Moshchot Coop, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "account",
        "account_payment_mode",
        "payment",
    ],
    "data": [
        "views/templates.xml",
        "data/payment_provider.xml",
        "security/ir.model.access.csv",
        "security/l10n_il_sumit_security.xml",
        "views/sumit_account.xml",
        "views/account_journal.xml",
        "views/account_payment.xml",
        "views/account_payment_method.xml",
        "views/payment_provider.xml",
    ],
    "demo": [],
    "external_dependencies": {
        "python": [
            "strenum",
        ],
    },
}
