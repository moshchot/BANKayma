import {registry} from "@web/core/registry";

export function bankayma_website_sale_frontend_steps() {
    return [
        {
            content: "Open the project dropdown",
            trigger: "#bk_project_dropdown",
            run: "click",
        },
        {
            content: "Select first project (B2B)",
            trigger: "#bk_project_dropdown + div.dropdown-menu > div > a",
            run: "click",
        },
        {
            content: "Wait for reload showing project badge",
            trigger: "div.products_header a.badge",
            run: () => {
                // Do nothing
            },
        },
        {
            content: "Search for B2B product",
            trigger: "input.search-query",
            run: "fill B2B product",
        },
    ];
}

registry.category("web_tour.tours").add("bankayma_website_sale_frontend", {
    url: "/shop",
    steps: () => bankayma_website_sale_frontend_steps({}),
});
