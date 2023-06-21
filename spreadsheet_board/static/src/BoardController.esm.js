/** @odoo-module
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {BoardArchParser} from "@board/board_view";
import {BoardController} from "@board/board_controller";
import {SpreadsheetBoard} from "@spreadsheet_board/SpreadsheetBoard.esm";
import {patch} from "@web/core/utils/patch";

BoardController.components.SpreadsheetBoard = SpreadsheetBoard;

patch(BoardArchParser.prototype, "parse spreadsheet_board properties", {
    parse(arch, customViewId) {
        const archInfo = this._super.apply(this, [arch, customViewId]); // eslint-disable-line no-useless-call
        let columnIndex = -1,
            rowIndex = -1;
        this.visitXML(arch, (node) => {
            switch (node.tagName) {
                case "column":
                    columnIndex++;
                    rowIndex = -1;
                    break;
                case "action": {
                    rowIndex++;
                    const action = archInfo.columns[columnIndex].actions[rowIndex];
                    if (action.viewMode === "spreadsheet_board") {
                        action.style = node.getAttribute("style");
                    }
                }
            }
        });
        return archInfo;
    },
});
