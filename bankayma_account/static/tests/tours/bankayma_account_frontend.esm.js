import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("bankayma_account_vendor_portal", {
    url: "/my",
    steps: () => [
        {
            content: "Click 'Edit information'",
            trigger: "a[href='/my/account']",
            run: "click",
        },
        {
            content: "Fill in a VAT",
            trigger: "input[name='vat']",
            run: "edit 234567899",
        },
        {
            content: "Fill in phone number",
            trigger: "input[name='phone']",
            run: "edit 123456789",
        },
        {
            content: "Fill in bank branch code",
            trigger: "input[name='bank_branch_code']",
            run: "edit 424242",
        },
        {
            content: "Fill in bank account number",
            trigger: "input[name='bank_acc_number']",
            run: "edit 424242",
        },
        {
            content: "Save form",
            trigger: "button[type='submit']",
            run: "click",
        },
        {
            content: "Click 'Your Invoices'",
            trigger: "a[href='/my/invoices']",
            run: "click",
        },
        {
            content: "Click 'Pay Me'",
            trigger: "a[href='/my/invoices/new']",
            run: "click",
        },
        {
            content: "Select first available project",
            trigger: "select#operating_unit_id",
            run: "selectByIndex 1",
        },
        {
            content: "Fill in description",
            trigger: "input[name='description']",
            run: "edit Some description",
        },
        {
            content: "Fill in amount",
            trigger: "input[name='amount']",
            run: "edit 4242",
        },
        {
            content: "Save form",
            trigger: "button[type='submit']",
            run: "click",
        },
    ],
});
