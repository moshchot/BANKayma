# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sumit_id = fields.Char()

    def _to_sumit_vals(self):
        """Return a dict describing this partner for sumit"""
        self.ensure_one()
        return (
            {
                "ExternalIdentifier": str(self.id),
                "NoVAT": None,
                "SearchMode": 0,
                "Name": self.display_name,
                "Phone": self.phone or None,
                "EmailAddress": self.email or None,
                "City": self.city or None,
                "Address": self.street or None,
                "ZipCode": self.zip or None,
                "CompanyNumber": None,
                "ID": None,
                "Folder": None,
            }
            if not self.sumit_id
            else {"ID": self.sumit_id}
        )
