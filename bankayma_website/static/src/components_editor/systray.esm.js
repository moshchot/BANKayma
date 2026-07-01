import {patch} from "@web/core/utils/patch";
import {systrayItem as systrayItemEditBackend} from "@website/systray_items/edit_in_backend";
import {systrayItem as systrayItemEditWebsite} from "@website/systray_items/edit_website";

patch(systrayItemEditWebsite, {
    isDisplayed(env) {
        const result = super.isDisplayed(...arguments);
        return result && env.services.website.bankayma_editable;
    },
});

patch(systrayItemEditBackend, {
    isDisplayed(env) {
        const result = super.isDisplayed(...arguments);
        return result && env.services.website.bankayma_editable;
    },
});
