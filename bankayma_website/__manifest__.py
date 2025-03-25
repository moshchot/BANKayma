# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (website)",
    "summary": "BANKayma website customizations",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "depends": [
        "bankayma_account",
        "website",
    ],
    "data": [
        "views/templates.xml",
        "views/res_company.xml",
    ],
    "demo": [],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {
        "python": [
            "acme>1.0.0,<2.0.0",
            "cryptography<43,>=41.0.5",
            "pyopenssl<23.0,>=22.1",
            "python-jose",
        ]
    },
}
