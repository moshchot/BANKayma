# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http

from odoo.addons.web.controllers.home import Home as _Home


class Home(_Home):
    def _login_redirect(self, uid, redirect=None):
        """Override redirect if we're logging in a user with a custom redirect"""
        user = http.request.env["res.users"].sudo().browse(uid)
        if not redirect and user.login_redirect:
            redirect = user.login_redirect
        response = super()._login_redirect(uid, redirect=redirect)
        if isinstance(response, str) and "#" not in response:
            response += "#cids=" + ",".join(map(str, user.company_ids.ids))
        return response
