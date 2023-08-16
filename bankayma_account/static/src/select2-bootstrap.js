(function () {
    "use strict";
    jQuery(document).ready(function () {
        // Bankayma specific
        jQuery("input[onchange]").change();
        // The rest should go to website_select2_bootstrap
        jQuery("select.o-select2").select2({
            theme: "bootstrap-5",
        });
    });
})();
