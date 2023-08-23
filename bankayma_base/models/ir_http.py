# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.http import request


class ResUsers(models.AbstractModel):
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
