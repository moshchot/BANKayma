/** @odoo-module **/

import {patch} from "web.utils";
import {websiteService} from "@website/services/website_service";

patch(websiteService, "bankayma_website", {
    async start() {
        const result = await this._super(...arguments);

        patch(result, "bankayma_website", {
            // eslint-disable-next-line accessor-pairs
            set pageDocument(doc) {
                this.bankayma_editable =
                    doc && doc.documentElement.dataset.bankayma_editable === "1";
                this._super(doc);
            },
        });
        return result;
    },
});
