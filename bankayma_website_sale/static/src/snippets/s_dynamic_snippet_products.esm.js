import DynamicSnippetProducts from "@website_sale/snippets/s_dynamic_snippet_products/000";

DynamicSnippetProducts.include({
    _getSearchDomain: function () {
        const domain = this._super();
        const operating_unit_id = this.$el.data("operating-unit-id");
        if (operating_unit_id) {
            domain.push([
                "operating_unit_id",
                "=",
                Number.parseInt(operating_unit_id, 10),
            ]);
        }
        return domain;
    },
});
