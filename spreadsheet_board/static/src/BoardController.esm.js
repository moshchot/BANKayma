/*
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {BoardArchParser} from "@board/board_view";
import {BoardController} from "@board/board_controller";
import {SpreadsheetBoard} from "@spreadsheet_board/SpreadsheetBoard.esm";
import {patch} from "@web/core/utils/patch";
import {visitXML} from "@web/core/utils/xml";

BoardController.components.SpreadsheetBoard = SpreadsheetBoard;

patch(BoardArchParser.prototype, {
    parse(arch) {
        const archInfo = super.parse(...arguments);
        let columnIndex = -1,
            rowIndex = -1;
        visitXML(arch, (node) => {
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
