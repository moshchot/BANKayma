import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("operating_unit_switcher_with_menu", {
    steps: () => [
        {
            content: "Observe menu exists",
            trigger: ".o_switch_ou_menu",
        },
    ],
});

registry.category("web_tour.tours").add("operating_unit_switcher_without_menu", {
    steps: () => [
        {
            content: "Observe menu does not exist",
            trigger: ".o_main_navbar",
            run: function (helper) {
                if (helper.anchor.querySelector(".o_switch_ou_menu")) {
                    throw new Error("OU switcher unexpectedly found");
                }
            },
        },
    ],
});
