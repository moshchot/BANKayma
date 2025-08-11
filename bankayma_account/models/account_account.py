# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    operating_unit_id = fields.Many2one("operating.unit")
    is_ou_specific = fields.Boolean(compute="_compute_is_ou_specific", store=True)

    @api.depends("code", "operating_unit_id.code")
    def _compute_is_ou_specific(self):
        for this in self:
            this.is_ou_specific = (
                this.code
                and this.operating_unit_id.code
                and this.code.startswith(this.operating_unit_id.code)
            )

    def action_open_bankayma_sibling_accounts(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "name": self.env._("OU Siblings of %s", self.name),
            "domain": self._ou_sibling_domain(),
            "views": [(False, "list"), (False, "form")],
        }

    def _ou_sibling_domain(self):
        code_patterns = [
            this.code
            if not this.is_ou_specific
            else ("%" + this.code[len(this.operating_unit_id.code) :])
            for this in self
        ]
        return (["|"] * max(len(code_patterns) - 1, 0)) + [
            ("code", "like", pattern) for pattern in code_patterns
        ]

    def _create_ou_sibling(self, ous):
        result = self.browse([])
        for this in self:
            if self.search(
                [("operating_unit_id", "in", ous.ids)] + this._ou_sibling_domain()
            ):
                continue
            for ou in ous:
                result += this.copy(
                    {
                        "operating_unit_id": ou.id,
                        "code": ou.code + this.code[len(this.operating_unit_id.code) :],
                    }
                )
        return result
