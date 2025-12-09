/** @odoo-module **/
import concurrency from "web.concurrency";
import publicWidget from "web.public.widget";
import {qweb} from "web.core";

publicWidget.registry.bankaymaProjectsSearchbar = publicWidget.Widget.extend({
    events: {
        "click .nav [data-search-field]": "onClickSearchMenu",
        "click .badge": "onClickBadge",
        "click form .input-group .dropdown-menu li": "onClickSuggestion",
        "input input[type='search']": "onInput",
        submit: "onSubmit",
    },
    selector: ".bankayma_searchbar",
    init: function () {
        this._super.apply(this, arguments);
        this._drop_previous = new concurrency.DropPrevious();
        this.onInput = _.debounce(this.onInput, 400);
    },
    start: function () {
        const self = this;
        this.$('form input.badge[type="hidden"]').each(function () {
            const field = $(this).attr("name");
            for (const id of $(this).val().split(",")) {
                const $badge = self.$(
                    `.nav [data-search-field="${field}"][data-search-value="${id}"]`
                );
                if (!$badge.length) {
                    continue;
                }
                self.addBadge(field, $badge.data("search-value"), $badge.text());
            }
        });
    },
    getSuggestions: function () {
        this.updateForm();
        return this._rpc({
            route: this.$("form").data("suggestion-route"),
            params: Object.fromEntries(new FormData(this.$("form")[0])),
        });
    },
    handleSuggestions: function (suggestions) {
        const $container = this.$("form .input-group");
        $container.find(".dropdown-menu,button[data-bs-toggle]").remove();
        if (!suggestions.length) {
            return;
        }
        const $dropdown = $(
            qweb.render("bankayma_searchbar.suggestions", {
                suggestions: suggestions,
            })
        );
        $container.append($dropdown);
        $dropdown.filter("button").click();
    },
    addBadge: function (field, value, name) {
        if (
            !this.$(
                `.badge[data-search-field="${field}"][data-search-value="${value}"]`
            ).length
        ) {
            $(
                qweb.render("bankayma_searchbar.badge", {
                    field: field,
                    name: name,
                    value: value,
                })
            ).insertBefore(this.$("form"));
        }
    },
    updateForm: function () {
        const self = this;
        this.$('form input.badge[type="hidden"]').each(function () {
            $(this).val(
                $.map(
                    self.$(`.badge[data-search-field="${$(this).attr("name")}"]`),
                    (el) => $(el).data("search-value")
                ).join(",")
            );
        });
    },
    onClickBadge: function (ev) {
        $(ev.target).remove();
        this.$("form").submit();
    },
    onClickSearchMenu: function (ev) {
        this.addBadge("tags", $(ev.target).data("search-value"), $(ev.target).text());
        this.$("form").submit();
    },
    onClickSuggestion: function (ev) {
        if ($(ev.currentTarget).data("search-field")) {
            const field = $(ev.currentTarget).data("search-field");
            const value = $(ev.currentTarget).data("search-value");
            this.$("input[type='search']").val("");
            this.$(
                `.nav [data-search-field="${field}"][data-search-value="${value}"]`
            ).click();
        }
    },
    onInput: function () {
        this._drop_previous
            .add(this.getSuggestions())
            .then(this.handleSuggestions.bind(this));
    },
    onSubmit: function (ev) {
        this.updateForm();
        ev.preventDefault();
        $.ajax(this.$("form").attr("action"), {
            data: new FormData(this.$("form")[0]),
            processData: false,
            contentType: false,
            type: "POST",
        }).then(function (html) {
            const $html = $($.parseHTML(html)),
                $current = $(document);
            const $new_results_section = $html.find("main section#results");
            const $new_no_results_section = $html.find(
                "main section#results + section"
            );
            const $results_section = $current.find("main section#results");
            const $no_results_section = $current.find("main section#results + section");
            $results_section.replaceWith($new_results_section);
            $no_results_section.replaceWith($new_no_results_section);
        });
    },
});
