# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse, urlunparse

from odoo import http

from odoo.addons.web.controllers.home import Home as _Home


class Home(_Home):
    def _login_redirect(self, uid, redirect=None):
        """Override redirect if we're logging in a user with a custom redirect"""
        user = http.request.env["res.users"].sudo().browse(uid)
        response = super()._login_redirect(uid, redirect=redirect)
        if isinstance(response, str):
            parsed = urlparse(response)
            if parsed.fragment.startswith("cids="):
                response = urlunparse(parsed[:5] + (f"cids={user.company_id.id}",))
        return response
