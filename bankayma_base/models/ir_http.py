# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _frontend_pre_dispatch(cls):  # pylint: disable=missing-return
        super()._frontend_pre_dispatch()
        request.update_context(
            allowed_company_ids=request.env.user.company_ids.ids,
        )
        request.website = (
            # pylint: disable=context-overridden
            request.env["website"]
            .get_current_website()
            .with_context(request.context)
        )

    def session_info(self):
        result = super().session_info()
        if "user_companies" in result:
            ResCompany = self.env["res.company"]
            result["user_companies"]["allowed_companies"] = {
                company_id: company_vals
                for company_id, company_vals in result["user_companies"][
                    "allowed_companies"
                ].items()
                if not ResCompany.browse(company_id).category_id
                or ResCompany.browse(company_id).category_id.show_in_company_selector
            }
        return result
