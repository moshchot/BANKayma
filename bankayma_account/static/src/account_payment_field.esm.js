/** @odoo-module
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import session from "web.session";

patch(registry.category("fields").get("payment").prototype, "hide unreconcile button", {
    setup() {
        onWillStart(async () => {
            this.show_unreconcile_button =
                (await session.user_has_group("bankayma_base.group_org_manager")) ||
                (await session.user_has_group("bankayma_base.group_full"));
        });
        var result = this._super.apply();
        var original_add = this.popover.add;
        var self = this;
        this.popover.add = function (target, Component, props, options = {}) {
            return original_add.apply(this, [
                target,
                Component,
                {show_unreconcile_button: self.show_unreconcile_button, ...props},
                options,
            ]);
        };
        return result;
    },
});
