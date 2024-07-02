# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class L10nIlHashavshevetConfigHeshin(models.Model):
    _inherit = "l10n.il.hashavshevet.config"
    _name = "l10n.il.hashavshevet.config.heshin"
    _description = "Hashavshevet export configuration - heshin"

    expr_key = fields.Char(hashavshevet_name="key", string="Account key")
    expr_name = fields.Char(hashavshevet_name="name", string="Account name")
    expr_sort_code = fields.Char(hashavshevet_name="sort_code", string="Sort code")
    expr_filter = fields.Char(hashavshevet_name="filter", string="Filter")

    expr_key_result = fields.Char(compute="_compute_results")
    expr_name_result = fields.Char(compute="_compute_results")
    expr_sort_code_result = fields.Char(compute="_compute_results")
    expr_filter_result = fields.Char(compute="_compute_results")
