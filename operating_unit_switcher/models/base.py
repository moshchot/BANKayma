# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from psycopg2.extras import Json as psycopg2_json

from odoo import models
from odoo.osv import expression
from odoo.tools import SQL

from .. import fields as ou_fields


class Base(models.AbstractModel):
    _inherit = "base"

    def with_ou(self, ou):
        return (
            self.with_context(
                allowed_ou_ids=ou.ids, default_operating_unit_id=ou[:1].id
            )
            if ou
            else self
        )

    def _read_group_groupby(self, groupby_spec, query):
        field_name, _property, _func = models.parse_read_group_spec(groupby_spec)
        if field_name in self._fields and isinstance(
            self._fields[field_name], ou_fields.OUSpecificField
        ):
            return SQL(
                "COALESCE(%(field_name)s->%(ou_id)s, %(field_name)s->'0')",
                field_name=SQL.identifier(field_name),
                ou_id=str(self.env.context.get("default_operating_unit_id")),
            )
        return super()._read_group_groupby(groupby_spec, query)

    def _condition_to_sql(self, alias, fname, operator, value, query):
        if fname in self._fields and isinstance(
            self._fields[fname], ou_fields.OUSpecificField
        ):
            return SQL(
                """
                COALESCE(
                    %(field_name)s->%(ou_id)s,
                    %(field_name)s->'0'
                ) %(operator)s %(value)s
                """,
                field_name=SQL.identifier(alias, fname),
                ou_id=str(self.env.context.get("default_operating_unit_id")),
                operator=expression.SQL_OPERATORS[operator],
                value=psycopg2_json(value),
            )
        return super()._condition_to_sql(alias, fname, operator, value, query)
