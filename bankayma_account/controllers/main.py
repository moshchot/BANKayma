# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields
from odoo.http import request

from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def __init__(self):
        self.OPTIONAL_BILLING_FIELDS.append("property_account_position_id")
        super().__init__()

    def _prepare_portal_layout_values(self):
        result = super()._prepare_portal_layout_values()
        result["fiscal_positions"] = (
            request.env["account.fiscal.position"]
            .sudo()
            .search(
                [
                    ("company_id", "=", request.env.company.id),
                ]
            )
        )
        return result

    def on_account_update(self, values, partner):
        for field_name in {"property_account_position_id"} & values.keys():
            try:
                values[field_name] = int(values[field_name])
            except BaseException:
                values[field_name] = False
        return values

    def _get_account_searchbar_filters(self):
        result = super()._get_account_searchbar_filters()
        result.update(
            paid={
                "label": _("Paid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("in_payment", "paid")),
                ],
            },
            unpaid={
                "label": _("Unpaid"),
                "domain": [
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                ],
            },
            late={
                "label": _("Overdue"),
                "domain": [
                    (
                        "invoice_date_due",
                        "<",
                        fields.Date.context_today(request.env.user),
                    ),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                ],
            },
        )
        return result
