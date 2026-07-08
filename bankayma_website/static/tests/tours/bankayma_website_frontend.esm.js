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
    url: "/event",
    steps: () => [
        {
            content: "Open the first event",
            trigger: "#o_wevent_index_main_col a",
            run: "click",
        },
        {
            content: "Be sure event is opened",
            trigger: "#o_wevent_event_main_cover_content",
        },
    ],
});
