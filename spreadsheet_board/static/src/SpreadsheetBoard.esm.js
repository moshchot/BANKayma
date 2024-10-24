/** @odoo-module
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {getBundle, loadBundle} from "@web/core/assets";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
const {Component, onWillStart, onWillRender, useRef} = owl;

export class SpreadsheetBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.container = useRef("container");
        onWillStart(async () => {
            // TODO no better way to lazy load this?
            const desc = await getBundle("spreadsheet.o_spreadsheet");
            await loadBundle(desc);
            await odoo.__DEBUG__.services[
                "@spreadsheet/helpers/helpers"
            ].loadSpreadsheetDependencies();
            this.data_sources = new odoo.__DEBUG__.services[
                "@spreadsheet/data_sources/data_sources"
            ].DataSources(this.orm);
            let result = null;
            try {
                result = await this.orm.read(
                    "spreadsheet.dashboard",
                    [this.props.action.actionId],
                    ["raw"]
                );
            } catch {
                console.log("Unable to load dashboard " + this.props.action.actionId);
            }
            this.data = (result && result[0].raw && JSON.parse(result[0].raw)) || null;
        });
    }
    get spreadsheet_component() {
        const Spreadsheet = window.o_spreadsheet.Spreadsheet;
        const container = this.container;
        class DashboardSpreadsheet extends Spreadsheet {}
        patch(DashboardSpreadsheet.prototype, "calculate dashboard height", {
            setup() {
                onWillRender(() => {
                    const {height} = this.model.getters.getMainViewportRect();
                    if (container.el) {
                        const $container = jQuery(container.el);
                        const current_height = $container.height();
                        if (current_height !== height) {
                            $container.height(height);
                        }
                    }
                });
                return this._super.apply(this, arguments);
            },
        });
        return DashboardSpreadsheet;
    }
    get spreadsheet_model() {
        if (this.model) {
            return this.model;
        }
        const model = new window.o_spreadsheet.Model(this.data, {
            evalContext: {env: this.env, orm: this.orm},
            mode: "dashboard",
            dataSources: this.data_sources,
        });
        this.data_sources.addEventListener("data-source-updated", () =>
            model.dispatch("EVALUATE_CELLS")
        );
        this.model = model;
        return model;
    }
    get spreadsheet_filters() {
        return this.spreadsheet_model.getters.getGlobalFilters();
    }
    get spreadsheet_filter_component() {
        return odoo.__DEBUG__.services[
            "@spreadsheet/global_filters/components/filter_value/filter_value"
        ].FilterValue;
    }
}

SpreadsheetBoard.template = "spreadsheet_board.SpreadsheetBoard";
