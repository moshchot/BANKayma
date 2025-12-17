/** @odoo-module **/
import {extraMenuUpdateCallbacks} from "website.content.menu";

function resetStickyTop() {
    const $header = jQuery(".o_header_fixed.o_top_fixed_element");
    const $search = jQuery(
        ".bankayma_event_searchbar,.bankayma_searchbar,div.products_header"
    );
    if ($header.length && $search.length) {
        if ($header.hasClass("o_header_is_scrolled")) {
            $search.css("padding-top", `${$header.outerHeight()}px`);
        } else {
            $search.css("padding-top", "");
        }
    }
}

extraMenuUpdateCallbacks.push(resetStickyTop);
