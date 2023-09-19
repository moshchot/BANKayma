(function () {
    "use strict";
    jQuery(document).ready(function () {
        jQuery("select[onchange]").change();
        jQuery(".bk-onchange").change(function () {
            var data = jQuery('select[name="property_account_position_id"]')
                    .find("option:selected")
                    .data(),
                $max_amount = jQuery("#bankayma_vendor_max_amount"),
                $tax_deduction = jQuery("#bankayma_vendor_tax_deduction"),
                $tax_percentage = jQuery("#bankayma_vendor_tax_percentage");

            $tax_percentage.prop("required", data.deduct_tax_use_max_amount === "True");
            $tax_percentage.parent().toggle(data.deduct_tax === "True");
            $max_amount.prop("required", data.deduct_tax_use_max_amount === "True");
            $max_amount.parent().toggle(data.deduct_tax_use_max_amount === "True");

            $tax_deduction.parent().toggle(data.deduct_tax_use_max_amount !== "True");
            $tax_percentage.toggle(
                data.deduct_tax_use_max_amount === "True" ||
                    $tax_deduction.prop("checked")
            );
            $tax_percentage.val(
                $tax_deduction.prop("checked") ? $tax_percentage.val() : 0
            );

            jQuery(".optional-tax-group").hide();
            (data.optional_tax_groups || []).forEach(function (tax_group_id) {
                jQuery("#tax_group_" + tax_group_id)
                    .parent()
                    .parent()
                    .show();
            });
        });
        jQuery(".bk-onchange").change();
    });
})();
