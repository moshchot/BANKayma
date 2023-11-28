# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CommentWizard(models.TransientModel):
    """This is the wizard of base_tier_validation for filling in a comment"""

    _inherit = "comment.wizard"

    def add_comment(self):
        """Switch to list view after posting comment"""
        result = super().add_comment()
        if not result and self.res_model == "account.move":
            return {
                "type": "ir.actions.act_multi",
                "actions": [
                    {"type": "ir.actions.act_window_close"},
                    {"type": "ir.actions.act_window.page.list"},
                ],
            }
        return result
