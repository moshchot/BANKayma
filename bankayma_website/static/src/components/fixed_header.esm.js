import {extraMenuUpdateCallbacks} from "@website/js/content/menu";

function resetStickyTop() {
    const $header = jQuery("#top");
    const $search = jQuery(
        ".bankayma_event_searchbar,.bankayma_searchbar,.bankayma_products_searchbar"
    );
    if ($header.length && $search.length) {
        if ($header.hasClass("o_header_is_scrolled") && $header.is(":visible")) {
            $search.css(
                "transform",
                `translate(0px, ${$header.outerHeight() + $header.position().top}px)`
            );
        } else {
            $search.attr("style", null);
        }
    }
}

extraMenuUpdateCallbacks.push(resetStickyTop);
