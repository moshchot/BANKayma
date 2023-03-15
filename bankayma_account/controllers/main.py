# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
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