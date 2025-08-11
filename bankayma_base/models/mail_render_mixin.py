# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    @api.model
    def _render_eval_context(self):
        result = super()._render_eval_context()
        alias_domain = self.env.company.alias_domain_id or self.env[
            "mail.alias.domain"
        ].search([], limit=1)
        result["catchall_address"] = alias_domain.catchall_alias
        return result
