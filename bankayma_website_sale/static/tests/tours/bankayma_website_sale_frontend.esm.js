import {registry} from "@web/core/registry";

export function bankayma_website_sale_frontend_steps() {
    return [
        /*
        {
            content: "Select the first challenge",
            trigger: "main .card a[href$='-1']",
            run: "click",
        },
        {
            content: "Click the pledge button",
            trigger: "main .nav a[href$='crowdfunding/1/pay']",
            run: "click",
        },
        {
            content: "Fill in your name",
            trigger: "input#name",
            run: "fill Firstname Lastname",
        },
        */
    ];
}

registry.category("web_tour.tours").add("bankayma_website_sale_frontend", {
    test: true,
    url: "/shop",
    steps: () => bankayma_website_sale_frontend_steps({}),
});
