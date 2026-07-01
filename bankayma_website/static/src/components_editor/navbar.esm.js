import {NavBar} from "@web/webclient/navbar/navbar";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

const systrayRegistry = registry.category("systray");

patch(NavBar.prototype, {
    get systrayItems() {
        const result = super.systrayItems;
        const ouSwitcher = systrayRegistry.get("SwitchOuMenu");
        return result.map((x) =>
            x.key === "WebsiteSwitcher"
                ? {
                      ...x,
                      key: "SwitchCompanyMenu",
                      ...ouSwitcher,
                  }
                : x
        );
    },
});
