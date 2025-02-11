# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_header = fields.Html(translate=True)
    company_details = fields.Html(translate=True)
    parent_root_id = fields.Many2one("res.company", compute="_compute_parent_root_id")

    def _compute_parent_root_id(self):
        for this in self:
            root = this.parent_id
            while root.parent_id:
                root = root.parent_id
            this.parent_root_id = root
