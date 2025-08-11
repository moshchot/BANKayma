import DynamicSnippet from "@website/snippets/s_dynamic_snippet/000";

DynamicSnippet.include({
    _fetchData: async function () {
        const result = await this._super();
        if (!this.data.length && this.$el.data("remove-if-empty")) {
            jQuery(this.$el.data("remove-if-empty")).remove();
        }
        return result;
    },
});
