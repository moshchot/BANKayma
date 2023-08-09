# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    use_sumit = fields.Boolean("Push paid invoices to sumit")
