import {registry} from "@web/core/registry";

export const OuColorService = {
    dependencies: ["ou_company"],

    async start(env, {ou_company}) {
        const bodyElement = window.document.body;
        bodyElement.dataset.ouId = ou_company.currentCompany.id;

        return {
            bodyElement,
        };
    },
};

registry.category("services").add("ou_color", OuColorService);
