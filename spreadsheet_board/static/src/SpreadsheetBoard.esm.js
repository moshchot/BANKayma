/*
 * Copyright 2023 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {loadBundle} from "@web/core/assets";
import {loadSpreadsheetDependencies} from "@spreadsheet/assets_backend/helpers";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
const {Component, onWillStart, onWillRender, useRef} = owl;
import {ControlPanel} from "@web/search/control_panel/control_panel";

export class SpreadsheetBoard extends Component {
    static template = "spreadsheet_board.SpreadsheetBoard";
    static components = {
        ControlPanel,
    };
    setup() {
        this.orm = useService("orm");
        this.container = useRef("container");
        onWillStart(async () => {
            await this.fetchSpreadsheetData();
            await this.setupDependencies();
            await this.setupModel();
            await this.setupComponents();
        });
    }
    async fetchSpreadsheetData() {
        let result = null;
        try {
            result = await this.orm.read(
                "spreadsheet.dashboard",
                [this.props.action.actionId],
                ["spreadsheet_data"]
            );
        } catch {
            console.log("Unable to load dashboard " + this.props.action.actionId);
        }
        this.data =
            (result &&
                result[0].spreadsheet_data &&
                JSON.parse(result[0].spreadsheet_data)) ||
            null;
    }
    async setupDependencies() {
        await loadSpreadsheetDependencies();
        await loadBundle("spreadsheet.o_spreadsheet");
    }
    async setupModel() {
        const OdooDataProvider = await odoo.loader.modules.get(
            "@spreadsheet/data_sources/odoo_data_provider"
        ).OdooDataProvider;
        const Model = await odoo.loader.modules.get(
            "@spreadsheet/o_spreadsheet/o_spreadsheet"
        ).Model;
        const provider = new OdooDataProvider(this.env);
        const model = new Model(this.data, {
            custom: {env: this.env, orm: this.orm, odooDataProvider: provider},
            mode: "dashboard",
        });
        provider.addEventListener("data-source-updated", () =>
            model.dispatch("EVALUATE_CELLS")
        );
        this.SpreadsheetModel = model;
    }
    async setupComponents() {
        const Spreadsheet = await odoo.loader.modules.get(
            "@spreadsheet/o_spreadsheet/o_spreadsheet"
        ).Spreadsheet;
        const container = this.container;
        class DashboardSpreadsheet extends Spreadsheet {}
        patch(DashboardSpreadsheet.prototype, {
            setup() {
                onWillRender(() => {
                    const {height} = this.model.getters.getMainViewportRect();
                    if (container.el) {
                        const current_height = container.el.offsetHeight;
                        if (current_height < height) {
                            container.el.style.height = `${height}px`;
                        }
                    }
                });
                return super.setup(arguments);
            },
        });
        this.SpreadsheetComponent = DashboardSpreadsheet;
        SpreadsheetBoard.components.FilterValue = await odoo.loader.modules.get(
            "@spreadsheet/global_filters/components/filter_value/filter_value"
        ).FilterValue;
    }
    get spreadsheet_filters() {
        return this.SpreadsheetModel.getters.getGlobalFilters();
    }
}
