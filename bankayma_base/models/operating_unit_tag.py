# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class OperatingUnitTag(models.Model):
    _name = "operating.unit.tag"
    _description = "Tags for operating units"
    _parent_store = True

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one("operating.unit.tag")
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("operating.unit.tag", "parent_id")
    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "operating_unit_operating_unit_tag_rel",
        "operating_unit_tag_id",
        "operating_unit_id",
    )

    def _compute_display_name(self):
        for this in self:
            this.display_name = "/".join(
                self.browse(
                    map(int, filter(None, (this.parent_path or "").split("/")))
                ).mapped("name")
            )
