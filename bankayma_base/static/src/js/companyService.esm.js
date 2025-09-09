/** @odoo-module **/

import {companyService} from "@web/webclient/company_service";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(companyService, "bankayma_base", {
    start() {
        const result = this._super(...arguments);
        result.hidden_company_ids = session.hidden_company_ids;
        return result;
    },
});
