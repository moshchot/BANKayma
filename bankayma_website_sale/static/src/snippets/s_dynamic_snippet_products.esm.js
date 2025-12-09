/** @odoo-module **/
import * as DynamicSnippetProducts from "website_sale.s_dynamic_snippet_products";

DynamicSnippetProducts.include({
    _getSearchDomain: function () {
        const domain = this._super();
        const company_id = this.$el.data("company-id");
        if (company_id !== null) {
            domain.push([
                "bankayma_website_sale_company_id",
                "=",
                Number.parseInt(company_id, 10),
            ]);
        }
        return domain;
    },
});
