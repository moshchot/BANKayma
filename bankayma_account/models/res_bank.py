# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class ResBank(models.Model):
    _inherit = "res.bank"

    def _constrain_provisioned(self):
        """Forbid editing/deleting banks that have been provisioned"""
        if self.env.is_system():
            return
        if self.env["ir.model.data"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                ("name", "not like", "__%"),
            ]
        ):
            raise exceptions.AccessError(
                _(
                    "You cannot change provisioned banks",
                )
            )

    def write(self, vals):
        """Forbid editing/deleting banks that have been provisioned"""
        self._constrain_provisioned()
        return super().write(vals)

    def unlink(self):
        self._constrain_provisioned()
        return super().unlink()
