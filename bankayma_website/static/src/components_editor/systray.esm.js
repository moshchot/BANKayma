/** @odoo-module **/

import {patch} from "web.utils";
import {systrayItem as systrayItemEditBackend} from "@website/systray_items/edit_in_backend";
import {systrayItem as systrayItemEditWebsite} from "@website/systray_items/edit_website";

patch(systrayItemEditWebsite, "bankayma_website", {
    isDisplayed(env) {
        const result = this._super(...arguments);
        return result && env.services.website.bankayma_editable;
    },
});

patch(systrayItemEditBackend, "bankayma_website", {
    isDisplayed(env) {
        const result = this._super(...arguments);
        return result && env.services.website.bankayma_editable;
    },
});
