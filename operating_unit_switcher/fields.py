# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
import collections

from psycopg2.extras import Json as psycopg2_json

from odoo import fields


class OUSpecificField:
    _column_type = ("jsonb", "jsonb")

    def convert_to_cache(self, value, record, validate=True):
        def super_convert(val):
            return super(OUSpecificField, self).convert_to_cache(
                val, record, validate=validate
            )

        if isinstance(value, collections.abc.Mapping):
            return {str(key): super_convert(val) for key, val in value.items()}
        if "default_operating_unit_id" not in record.env.contect:
            raise ValueError(
                "You cannot set a scalar value without default OU in the context"
            )
        ou_id = record.context["default_operating_unit_id"]
        vals = dict(record._cache.get(self) or {})
        vals[str(ou_id)] = super_convert(value)
        return vals

    def convert_to_column(self, value, record, values=None, validate=True):
        return psycopg2_json(value)

    def convert_to_record(self, value, record):
        return self.convert_to_read(value, record)

    def convert_to_read(self, value, record, use_display_name=True):
        if not isinstance(value, collections.abc.Mapping):
            # value has already been converted to read format
            return value
        return (
            value
            and value.get(str(record.env.context.get("default_operating_unit_id") or 0))
            or value.get("0")
            or False
        )

    def convert_to_write(self, value, record):
        return self.convert_to_cache(value, record)


class Selection(OUSpecificField, fields.Selection):
    pass
