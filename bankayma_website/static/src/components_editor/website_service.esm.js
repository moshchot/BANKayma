import {patch} from "@web/core/utils/patch";
import {websiteService} from "@website/services/website_service";

patch(websiteService, {
    async start() {
        const result = await super.start(...arguments);

        patch(result, {
            // eslint-disable-next-line accessor-pairs
            set pageDocument(doc) {
                this.bankayma_editable =
                    doc && doc.documentElement.dataset.bankayma_editable === "1";
                super.pageDocument = doc;
            },
        });
        return result;
    },
});
