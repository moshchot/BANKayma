# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import threading

from odoo import api, models

_logger = logging.getLogger("company_cascade")


class IrProperty(models.Model):
    _inherit = ["ir.property", "company.cascade.mixin", "company.cascade.up.mixin"]
    _name = "ir.property"
    _company_cascade_cascade_create = True
    _company_cascade_cascade_write = True

    @api.model
    def _set_multi(self, name, model, values, default_value=None):
        """Intercept sql delete"""
        thread = threading.current_thread()
        hooks = list(getattr(thread, "query_hooks", []))
        thread.query_hooks = hooks

        to_delete_ids = []

        def intercept_delete(cursor, query, params, start, delay):
            if isinstance(query, str) and query.startswith(
                "DELETE FROM ir_property WHERE id="
            ):
                to_delete_ids.extend(params)

        hooks.append(intercept_delete)

        result = super()._set_multi(name, model, values, default_value=default_value)

        thread.query_hooks = tuple(hook for hook in hooks if hook != intercept_delete)

        if to_delete_ids:
            self.browse(to_delete_ids).unlink()

        return result

    def _company_cascade_values(self, company, vals):
        """Special treatment for value_reference"""
        result = super()._company_cascade_values(company, vals)
        if "value_reference" in result and result["value_reference"]:
            result["value_reference"] = self._company_cascade_value_reference(
                company, None, self.get_by_record()
            )
        return result

    def _company_cascade_find_candidate(self, company, vals):
        result = self.search(
            [
                ("fields_id", "=", vals.get("fields_id")),
                ("res_id", "=", vals.get("res_id")),
                ("company_id", "=", company.id),
            ]
        )
        _logger.debug("find_candidate: returning %s", result)
        return result
