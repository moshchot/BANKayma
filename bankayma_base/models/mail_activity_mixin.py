# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    activity_ids = fields.One2many(groups="base.group_user,bankayma_base.group_income")
    activity_state = fields.Selection(
        groups="base.group_user,bankayma_base.group_income"
    )
    activity_user_id = fields.Many2one(
        groups="base.group_user,bankayma_base.group_income"
    )
    activity_type_id = fields.Many2one(
        groups="base.group_user,bankayma_base.group_income"
    )
    activity_date_deadline = fields.Date(
        groups="base.group_user,bankayma_base.group_income"
    )
    my_activity_date_deadline = fields.Date(
        groups="base.group_user,bankayma_base.group_income"
    )
    activity_summary = fields.Char(groups="base.group_user,bankayma_base.group_income")
