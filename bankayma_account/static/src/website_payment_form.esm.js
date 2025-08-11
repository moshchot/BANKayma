import {_t} from "@web/core/l10n/translation";
import checkoutForm from "@payment/js/payment_form";

checkoutForm.include({
    events: Object.assign({}, checkoutForm.prototype.events, {
        submit: "_submitDeactivated",
    }),
    _submitDeactivated: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
    },
    _submitForm: async function () {
        const $recurrency_confirmation = $(
            ".o_donation_payment_form #recurrency_confirmation"
        );
        if (
            $recurrency_confirmation.length &&
            !$recurrency_confirmation.is(":checked")
        ) {
            this._displayErrorDialog(
                _t("Validation Error"),
                _t("You need to agree to periodic withdrawals.")
            );
            return;
        }
        return this._super(...arguments);
    },
    _prepareTransactionRouteParams: function () {
        const result = this._super(...arguments);
        if (this.$("#tax_number").length) {
            result.tax_number = this.$("#tax_number").val();
        }
        if (this.$("input[name='operating_unit_id']").length) {
            result.operating_unit_id = parseInt(
                this.$("input[name='operating_unit_id']").val(),
                10
            );
        }
        return $(".o_donation_payment_form #recurrency_confirmation").length
            ? {
                  ...result,
                  is_recurrent: true,
              }
            : result;
    },
});
