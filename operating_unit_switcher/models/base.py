# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def with_ou(self, ou):
        return (
            self.with_context(
                allowed_ou_ids=ou.ids, default_operating_unit_id=ou[:1].id
            )
            if ou
            else self
        )
