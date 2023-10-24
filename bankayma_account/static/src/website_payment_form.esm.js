/** @odoo-module **/

import {_t} from "web.core";
import checkoutForm from "payment.checkout_form";

checkoutForm.include({
    _processPayment: function () {
        const $recurrency_confirmation = $(
            ".o_donation_payment_form #recurrency_confirmation"
        );
        if (
            $recurrency_confirmation.length &&
            !$recurrency_confirmation.is(":checked")
        ) {
            this._displayError(
                _t("Validation Error"),
                _t("You need to agree to periodic withdrawals.")
            );
            return Promise.resolve();
        }
        return this._super(...arguments);
    },
    _prepareTransactionRouteParams: function () {
        const result = this._super(...arguments);
        return $(".o_donation_payment_form #recurrency_confirmation").length
            ? {
                  ...result,
                  is_recurrent: true,
              }
            : result;
    },
});
