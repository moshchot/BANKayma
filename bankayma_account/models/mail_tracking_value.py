# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailTrackingValue(models.Model):
    _inherit = "mail.tracking.value"

    @api.model
    def create_tracking_values(
        self,
        initial_value,
        new_value,
        col_name,
        col_info,
        tracking_sequence,
        model_name,
    ):
        if col_name == "bankayma_move_line_analytic_distribution":
            field = self.env["ir.model.fields"]._get(model_name, col_name)

            def format_analytic_distribution(value):
                return (
                    "".join(
                        "%s: %s"
                        % (
                            self.env["account.analytic.account"]
                            .browse(int(account_id))
                            .display_name,
                            percentage,
                        )
                        for account_id, percentage in value.items()
                    )
                    if value
                    else ""
                )

            return {
                "field": field.id,
                "field_desc": col_info["string"],
                "field_type": col_info["type"],
                "tracking_sequence": tracking_sequence,
                "old_value_char": format_analytic_distribution(initial_value),
                "new_value_char": format_analytic_distribution(new_value),
            }
        else:
            return super().create_tracking_values(
                initial_value,
                new_value,
                col_name,
                col_info,
                tracking_sequence,
                model_name,
            )
