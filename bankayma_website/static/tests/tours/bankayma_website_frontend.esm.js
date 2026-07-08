import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("bankayma_website_frontend_news", {
    url: "/news",
    steps: () => [
        {
            content: "Open the first blog entry",
            trigger: "#o_wblog_posts_loop a",
            run: "click",
        },
        {
            content: "Be sure entry is opened",
            trigger: "#o_wblog_post_name",
        },
    ],
});

registry.category("web_tour.tours").add("bankayma_website_frontend_event", {
    steps: () => [
        {
            content: "Open event 'Great Reno Ballon Race'",
            trigger: "#o_wevent_index_main_col a[href*=reno]",
            run: "click",
        },
        {
            content: "Click register",
            trigger: "button[data-bs-target='#modal_ticket_registration']",
            run: "click",
        },
        {
            content: "Submit",
            trigger: "#o_wevent_tickets button[type='submit']",
            run: "click",
        },
        {
            content: "Fill in name",
            trigger: ".modal-body input[name*='-name-']",
            async run() {
                this.anchor.value = "Testname";
            },
        },
        {
            content: "Fill in email",
            trigger: ".modal-body input[name*='-email-']",
            async run() {
                this.anchor.value = "test@test.com";
            },
        },
        {
            content: "Submit",
            trigger: "#attendee_registration button[type='submit']",
            run: "click",
        },
        {
            content: "Wait for registration success page to be shown",
            trigger: ".o_wereg_confirmed",
        },
    ],
});
