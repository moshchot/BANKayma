# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bankayma_overhead_percentage = fields.Float(
        "Overhead percentage",
        compute="_compute_bankayma_overhead_percentage",
        inverse="_inverse_bankayma_overhead_percentage",
        compute_sudo=True,
    )

    def _compute_bankayma_overhead_percentage(self):
        for this in self:
            this.bankayma_overhead_percentage = max(
                self.env["account.journal"]
                .search(
                    [
                        ("bankayma_charge_overhead", "=", True),
                        ("company_id", "=", this.id),
                    ]
                )
                .mapped("bankayma_overhead_percentage")
                or [0]
            )

    def _inverse_bankayma_overhead_percentage(self):
        for this in self:
            self.env["account.journal"].search(
                [
                    ("bankayma_charge_overhead", "=", True),
                    ("company_id", "=", this.id),
                ]
            ).write(
                {
                    "bankayma_overhead_percentage": this.bankayma_overhead_percentage,
                }
            )
