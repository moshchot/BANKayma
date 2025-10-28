/** @odoo-module **/

import {NavBar} from "@web/webclient/navbar/navbar";
import {patch} from "web.utils";
import {registry} from "@web/core/registry";

const systrayRegistry = registry.category("systray");

patch(NavBar.prototype, "bankayma_website", {
    get systrayItems() {
        const result = this._super();
        const companySwitcher = systrayRegistry.get("SwitchCompanyMenu");
        return result.map((x) =>
            x.key === "WebsiteSwitcher"
                ? {
                      ...x,
                      key: "SwitchCompanyMenu",
                      ...companySwitcher,
                  }
                : x
        );
    },
});
