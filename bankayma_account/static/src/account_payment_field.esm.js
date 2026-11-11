/*
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {AccountPaymentField} from "@account/components/account_payment_field/account_payment_field";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

patch(AccountPaymentField.prototype, {
    setup() {
        onWillStart(async () => {
            this.show_unreconcile_button =
                (await user.hasGroup("bankayma_base.group_org_manager")) ||
                (await user.hasGroup("bankayma_base.group_full"));
        });
        var result = super.setup();
        var original_open = this.popover.open;
        var self = this;
        this.popover.open = function (target, props) {
            return original_open.apply(this, [
                target,
                {show_unreconcile_button: self.show_unreconcile_button, ...props},
            ]);
        };
        return result;
    },
});
