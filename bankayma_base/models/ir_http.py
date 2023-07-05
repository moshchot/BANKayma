# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import hashlib
import json

from odoo import models
from odoo.http import request
from odoo.tools import ustr


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session_info = super().session_info()
        if self.env.user.has_group("bankayma_base.group_income"):
            user = self.env.user
            menus = self.env["ir.ui.menu"].load_menus(request.session.debug)
            ordered_menus = {str(k): v for k, v in menus.items()}
            menu_json_utf8 = json.dumps(
                ordered_menus, default=ustr, sort_keys=True
            ).encode()
            session_info["cache_hashes"].update(
                {
                    "load_menus": hashlib.sha512(menu_json_utf8).hexdigest()[
                        :64
                    ],  # sha512/256
                }
            )
            session_info.update(
                {
                    # current_company should be default_company
                    "user_companies": {
                        "current_company": user.company_id.id,
                        "allowed_companies": {
                            comp.id: {
                                "id": comp.id,
                                "name": comp.name,
                                "sequence": comp.sequence,
                            }
                            for comp in user.company_ids
                        },
                    },
                    "show_effect": True,
                    "display_switch_company_menu": user.has_group(
                        "base.group_multi_company"
                    )
                    and len(user.company_ids) > 1,
                }
            )
        return session_info
