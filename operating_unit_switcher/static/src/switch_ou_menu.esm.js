import {useEnv, useSubEnv} from "@odoo/owl";
import {SwitchCompanyMenu} from "@web/webclient/switch_company_menu/switch_company_menu";
import {cookie} from "@web/core/browser/cookie";
import {registry} from "@web/core/registry";
import {router} from "@web/core/browser/router";
import {useService} from "@web/core/utils/hooks";
import {user} from "@web/core/user";

export const OuCompanyService = {
    // Provide the same interface as company service, but with OUs
    // depend on company to be sure start happens after company service has set up
    // allowed_company_ids
    dependencies: ["company", "orm"],

    async start(env, {orm}) {
        const ou_info = await orm.call(
            "res.users",
            "operating_unit_switcher_get_ou_info"
        );
        const ous = ou_info.operating_units;
        const ous_by_id = Object.fromEntries(ous.map((x) => [x.id, x]));
        const ou_ids = ous.map((x) => x.id);
        const ou_ids_cookie = (cookie.get("ou_ids") || "")
            .split("-")
            .filter((x) => x.length)
            .map(Number)
            .filter((x) => ou_ids.includes(x));
        const active_ou_ids = ou_ids_cookie.length
            ? ou_ids_cookie.slice()
            : ou_ids.slice();

        user.updateContext({allowed_ou_ids: active_ou_ids});
        if (active_ou_ids.length) {
            user.updateContext({default_operating_unit_id: active_ou_ids[0]});
        }

        return {
            allowedCompanies: ous_by_id,
            allowedCompaniesWithAncestors: ous_by_id,
            disallowedAncestorCompanies: {},

            get activeCompanyIds() {
                return active_ou_ids.slice();
            },

            get currentCompany() {
                return ous_by_id[active_ou_ids[0]];
            },

            getCompany(id) {
                return ous_by_id[id];
            },

            async setCompanies(companyIds) {
                cookie.set("ou_ids", companyIds.join("-"));
                user.updateContext({allowed_ou_ids: companyIds});
                router.pushState({}, {reload: true});
            },
        };
    },
};

export class SwitchOuMenu extends SwitchCompanyMenu {
    static template = "operating_unit_switcher.menu";

    setup() {
        const env = useEnv();
        const customServices = Object.assign({}, env.services);
        Object.assign(customServices, {company: useService("ou_company")});
        useSubEnv({
            services: customServices,
        });
        return super.setup();
    }
}

export const SystrayItem = {
    Component: SwitchOuMenu,
};

registry.category("systray").add("SwitchOuMenu", SystrayItem, {sequence: 0.5});
registry.category("services").add("ou_company", OuCompanyService);
