# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    @api.model
    def _render_eval_context(self):
        result = super()._render_eval_context()
        catchall_domain = (
            self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
        )
        catchall_alias = (
            self.env["ir.config_parameter"].sudo().get_param("mail.catchall.alias")
        )
        if catchall_domain and catchall_alias:
            result["catchall_address"] = f"{catchall_alias}@{catchall_domain}"
        else:
            result["catchall_address"] = False
        return result
