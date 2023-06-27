/** @odoo-module
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {BoardController} from "@board/board_controller";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_lt} from "@web/core/l10n/translation";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import session from "web.session";
import {useService} from "@web/core/utils/hooks";

patch(BoardController.prototype, "add impose on all users", {
    setup() {
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.show_button_impose_all_users = await session.user_has_group(
                "bankayma_base.group_org_manager"
            );
        });
        return this._super.apply();
    },
    button_impose_all_users() {
        this.dialog.add(ConfirmationDialog, {
            body: _lt("Really impose on all users?"),
            confirm: () => this.impose_all_users(),
            cancel: () => null,
        });
    },
    impose_all_users() {
        return this.orm.call("board.board", "action_impose_all_users");
    },
});
