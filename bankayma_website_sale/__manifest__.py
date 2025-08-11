# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BANKayma (website_sale)",
    "summary": "BANKayma website_sale customizations",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "author": "Moshchot Coop",
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "bankayma_account",
        "bankayma_website",
        "website_event_sale",
    ],
    "data": [
        "data/product_product.xml",
        "data/ir_config_parameter.xml",
        "data/website_snippet_filter.xml",
        "security/bankayma_website_sale.xml",
        "security/ir.model.access.csv",
        "templates/project_page.xml",
        "templates/project_page_embed.xml",
        # "templates/sale.xml",
        # "templates/website_event.xml",
        # "templates/website_sale.xml",
        # "views/event_event.xml",
        "views/menu.xml",
        "views/product_product.xml",
        "views/product_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            # "web/static/src/views/fields/many2many_tags/tags_list.scss",
            "bankayma_website_sale/static/src/snippets/*",
            # "bankayma_website_sale/static/src/scss/bankayma_website_sale.scss",
        ],
        "website.assets_editor": [
            # "bankayma_website_sale/static/src/components/bankayma_configure_tickets.*"
        ],
    },
    "demo": [
        "demo/product_product.xml",
    ],
    "website": "https://github.com/moshchot/BANKayma",
    "external_dependencies": {"python": []},
    "installable": True,
}
