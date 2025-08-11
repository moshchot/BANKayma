# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class OperatingUnitCategory(models.Model):
    _name = "operating.unit.category"
    _description = "Category for Operating Units"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    active = fields.Boolean(default=True)
    show_in_ou_selector = fields.Boolean(
        help="If this is disabled, companies in this category do not show in the "
        "OU selector, unless the user has group organization manager.",
        default=True,
    )
    parent_id = fields.Many2one(
        string="Parent Category",
        comodel_name="operating.unit.category",
    )
    parent_path = fields.Char(index=True)
    operating_unit_ids = fields.One2many("operating.unit", "category_id")
    operating_unit_count = fields.Integer(compute="_compute_operating_unit_count")

    def _compute_operating_unit_count(self):
        for this in self:
            this.operating_unit_count = len(this.operating_unit_ids)

    def action_show_ous(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "operating.unit",
            "views": [(False, "list"), (False, "form")],
            "domain": [("category_id", "in", self.ids)],
            "context": {
                "allowed_ou_ids": [],
            },
        }
