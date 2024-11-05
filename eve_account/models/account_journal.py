# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def init(self):
        result = super().init()
        self.__class__._company_cascade_exclude_fields = tuple(
            set(self._company_cascade_exclude_fields) | {"bankayma_overhead_percentage"}
        )
        return result
