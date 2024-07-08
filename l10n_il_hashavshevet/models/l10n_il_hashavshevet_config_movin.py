# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class L10nIlHashavshevetConfigMovin(models.Model):
    _inherit = "l10n.il.hashavshevet.config"
    _name = "l10n.il.hashavshevet.config.movin"
    _description = "Hashavshevet export configuration - movin"

    expr_code = fields.Char(hashavshevet_name="code", string="Traffic type code")
    expr_ref1 = fields.Char(hashavshevet_name="ref1", string="Reference 1")
    expr_date_ref = fields.Char(
        hashavshevet_name="date_ref", string="Date of reference"
    )
    expr_ref2 = fields.Char(hashavshevet_name="ref2", string="Reference 2")
    expr_date_value = fields.Char(hashavshevet_name="date_value", string="Value date")
    expr_currency = fields.Char(hashavshevet_name="currency", string="Currency code")
    expr_details = fields.Char(hashavshevet_name="details", string="Details")
    expr_left_account1 = fields.Char(
        hashavshevet_name="left_account1", string="Left account key 1"
    )
    expr_left_account2 = fields.Char(
        hashavshevet_name="left_account2", string="Left account key 2"
    )
    expr_right_account1 = fields.Char(
        hashavshevet_name="right_account1", string="Right account key 1"
    )
    expr_right_account2 = fields.Char(
        hashavshevet_name="right_account2", string="Right account key 2"
    )
    expr_left_account1_amount = fields.Char(
        hashavshevet_name="left_account1_amount", string="Left amount 1 in NIS"
    )
    expr_left_account2_amount = fields.Char(
        hashavshevet_name="left_account2_amount", string="Left amount 2 in NIS"
    )
    expr_right_account1_amount = fields.Char(
        hashavshevet_name="right_account1_amount", string="Right amount 1 in NIS"
    )
    expr_right_account2_amount = fields.Char(
        hashavshevet_name="right_account2_amount", string="Right amount 2 in NIS"
    )

    expr_code_result = fields.Char(compute="_compute_results")
    expr_ref1_result = fields.Char(compute="_compute_results")
    expr_ref2_result = fields.Char(compute="_compute_results")
    expr_date_ref_result = fields.Char(compute="_compute_results")
    expr_date_value_result = fields.Char(compute="_compute_results")
    expr_currency_result = fields.Char(compute="_compute_results")
    expr_details_result = fields.Char(compute="_compute_results")
    expr_left_account1_result = fields.Char(compute="_compute_results")
    expr_left_account2_result = fields.Char(compute="_compute_results")
    expr_right_account1_result = fields.Char(compute="_compute_results")
    expr_right_account2_result = fields.Char(compute="_compute_results")
    expr_left_account1_amount_result = fields.Char(compute="_compute_results")
    expr_left_account2_amount_result = fields.Char(compute="_compute_results")
    expr_right_account1_amount_result = fields.Char(compute="_compute_results")
    expr_right_account2_amount_result = fields.Char(compute="_compute_results")
