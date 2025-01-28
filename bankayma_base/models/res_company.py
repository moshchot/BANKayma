# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    name = fields.Char(
        translate=True,
    )
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        group = self.env.ref("bankayma_base.group_org_manager")
        self.env["res.users"].sudo().search([("groups_id", "=", group.id)]).write(
            {
                "company_ids": [(4, this.id) for this in result],
            }
        )
        return result

    def unlink(self):
        if self.env.user.id == SUPERUSER_ID:
            domain = [("company_id", "in", self.ids)]
            self.env["account.fiscal.position.tax"].search(domain).unlink()
            self.env["account.fiscal.position"].search(domain).unlink()
            self.env["account.tax"].search(domain).unlink()
            self.env["account.payment.mode"].search(domain).unlink()
            self.env["account.journal"].search(domain).unlink()
            self.env["account.account"].search(domain).unlink()
            self.env["ir.sequence"].search(domain).unlink()
            self.env["res.users"].search(domain).unlink()
        return super().unlink()
