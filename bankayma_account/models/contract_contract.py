from odoo import fields, models


class ContractContrac(models.Model):
    _inherit = "contract.contract"

    sumit_details = fields.Json()
