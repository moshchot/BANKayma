import portalDetails from "@portal/js/portal";
import publicWidget from "@web/legacy/js/public/public_widget";

portalDetails.include({
    events: Object.assign({}, portalDetails.prototype.events, {
        "change select[name='property_account_position_id']": "_onChangeTaxFields",
        "change input#bankayma_vendor_tax_deduction": "_onChangeTaxFields",
    }),
    start() {
        this._super(...arguments);
        this._onChangeTaxFields();
    },
    _onChangeTaxFields() {
        var data = this.$el
                .find('select[name="property_account_position_id"]')
                .find("option:selected")
                .data(),
            $max_amount = this.$el.find("#bankayma_vendor_max_amount"),
            $tax_percentage = this.$el.find("#bankayma_vendor_tax_percentage");

        $tax_percentage.prop("required", data.deduct_tax_use_max_amount === "True");
        $tax_percentage.parent().toggle(data.deduct_tax === "True");
        $max_amount.prop("required", data.deduct_tax_use_max_amount === "True");
        $max_amount.parent().toggle(data.deduct_tax_use_max_amount === "True");

        this.$el
            .find(".optional-tax-group")
            .toggle((data.optional_tax_groups || []).length > 0);
        this.$el.find(".optional-tax-group option").each(function (i, o) {
            var $o = jQuery(o);
            $o.toggle(
                $o.val() === "" ||
                    (data.optional_tax_groups || []).indexOf(parseInt($o.val(), 10)) >=
                        0
            );
        });
    },
});
publicWidget.registry.BankaymaNewVendorBill = publicWidget.Widget.extend({
    selector: ".o_portal_new_vendor_bill",
    events: {
        "change select[name='fpos']": "_onChangeFpos",
    },
    start() {
        this._super(...arguments);
        this._onChangeFpos();
    },
    _onChangeFpos() {
        const $option = this.$el.find("select[name='fpos'] option:selected");
        this.$el
            .find("#vendor_doc_description")
            .html($option.data("vendor_doc_description"));
        this.$el
            .find("#upload")
            .prop("required", $option.data("vendor_doc_mandatory") === "True");
    },
});
