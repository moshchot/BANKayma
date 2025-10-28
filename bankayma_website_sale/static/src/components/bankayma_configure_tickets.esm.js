/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component} = owl;

export class BankaymaConfigureTickets extends Component {
    setup() {
        this.websiteService = useService("website");
        this.actionService = useService("action");
    }

    async configureTickets() {
        const action = await this.actionService.loadAction(
            "bankayma_website_sale.action_bankayma_configure_tickets"
        );
        const {
            metadata: {mainObject},
        } = this.websiteService.currentWebsite;
        action.res_id = mainObject.id;
        return this.actionService.doAction(action, {
            onClose: () => {
                this.websiteService.goToWebsite();
            },
        });
    }
}
BankaymaConfigureTickets.template = "bankayma_website_sale.BankaymaConfigureTickets";

export const systrayItem = {
    Component: BankaymaConfigureTickets,
    isDisplayed: (env) =>
        env.services.website.currentWebsite &&
        env.services.website.currentWebsite.metadata.mainObject &&
        env.services.website.currentWebsite.metadata.mainObject.model === "event.event",
};

registry
    .category("website_systray")
    .add("BankaymaConfigureTickets", systrayItem, {sequence: 8});
