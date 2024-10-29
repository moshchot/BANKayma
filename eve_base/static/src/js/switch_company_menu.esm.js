/** @odoo-module **/
import {onWillStart, useState} from "@odoo/owl";
import {SwitchCompanyMenu} from "@web/webclient/switch_company_menu/switch_company_menu";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SwitchCompanyMenu.prototype, "EveCompanyMenu", {
    setup() {
        this._super();
        this.user = useService("user");
        this.state = useState({
            showCheckboxes: true,
            ...this.state,
        });

        onWillStart(async () => {
            this.state.showCheckboxes =
                !(await this.user.hasGroup("bankayma_base.group_manager")) ||
                (await this.user.hasGroup("bankayma_base.group_org_manager"));
        });
    },
});
