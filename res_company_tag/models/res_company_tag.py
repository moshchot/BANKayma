# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class ResCompanyTag(models.Model):
    _name = "res.company.tag"
    _description = "Tags for companies"
    _parent_store = True

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one("res.company.tag")
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("res.company.tag", "parent_id")

    def name_get(self):
        return [
            (
                this.id,
                "/".join(
                    self.browse(
                        map(int, filter(None, this.parent_path.split("/")))
                    ).mapped("name")
                ),
            )
            for this in self
        ]
