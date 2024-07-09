# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models, tools


class L10nIlHashavshevetConfig(models.AbstractModel):
    _name = "l10n.il.hashavshevet.config"
    _description = "Hashavshevet export configuration - abstract base class"
    _rec_name = "expr_condition"

    active = fields.Boolean(default=True)
    move_line_id = fields.Many2one("account.move.line")
    expr_condition = fields.Char("Condition")
    expr_condition_result = fields.Char(compute="_compute_results")

    def _compute_results_depends(self):
        return ("move_line_id", "expr_condition",) + tuple(
            field_name
            for field_name, field in self._fields.items()
            if getattr(field, "hashavshevet_name", False)
        )

    @api.depends(lambda self: self._compute_results_depends())
    def _compute_results(self):
        for field_name in self._compute_results_depends():
            if field_name + "_result" not in self._fields:
                continue
            try:
                self[field_name + "_result"] = self._eval_field(
                    self.move_line_id, field_name
                )
                if field_name == "expr_condition":
                    if self["expr_condition_result"]:
                        self["expr_condition_result"] = False
                    else:
                        self["expr_condition_result"] = _(
                            "Move line %(move_line_id)s does not match your condition "
                            "`%(expr_condition)s`"
                        ) % dict(
                            move_line_id=self.move_line_id.display_name,
                            expr_condition=self.expr_condition,
                        )
            except Exception as e:
                self[field_name + "_result"] = _(
                    "Error evaluating %(expression)s:\n%(message)s"
                ) % dict(
                    expression=self[field_name],
                    message=str(e),
                )

    def _eval_context(self, move_line):
        return {
            "line": move_line,
        }

    def _eval_field(self, move_line, field_name):
        eval_context = self._eval_context(move_line)
        return tools.safe_eval.safe_eval(
            self[field_name] or "False", locals_dict=eval_context
        )

    def _eval_all(self, move_line):
        return {
            field.hashavshevet_name: self._eval_field(move_line, field_name)
            for field_name, field in self._fields.items()
            if getattr(field, "hashavshevet_name", False)
        }

    def _valid_field_parameter(self, field, name):
        return (
            super()._valid_field_parameter(field, name) or name == "hashavshevet_name"
        )
