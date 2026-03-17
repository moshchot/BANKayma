# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from urllib.parse import quote

import werkzeug

from odoo import models
from odoo.tools import ustr

from odoo.addons.http_routing.models import ir_http


def slugify_one(s, max_length=0):
    result = ""
    s = re.sub(r"[-_\s]+", "-", ustr(s).lower())
    quoted = map(quote, s)
    for quoted_char in quoted:
        if not max_length or len(result) + len(quoted_char) <= max_length:
            result += quoted_char
        else:
            break
    return result


def unslug(s):
    slug = ""
    _id = ""

    if not s:
        return None, None

    for i in range(len(s) - 1, -1, -1):
        if s[i].isdigit():
            _id = s[i] + _id
        else:
            if s[i] == "-":
                _id = int(_id)
                slug = s[:i]
            else:
                slug, _id = None, None
            break
    return slug, _id


ir_http.slugify_one = slugify_one
ir_http.unslug = unslug


class ModelConverter(ir_http.ModelConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = r"(.*-)?\d+$"

    def to_url(self, value):
        # sudo the record we got to allow model(something) in routes and sudoing
        # afterwards
        return super().to_url(value.sudo())

    def to_python(self, value):
        _dummy, _id = unslug(value)
        if not _id:
            raise werkzeug.routing.ValidationError()
        return super().to_python(str(_id))


class IrHttp(models.AbstractModel):
    _inherit = ["ir.http"]

    @classmethod
    def _get_converters(cls):
        return dict(
            super(IrHttp, cls)._get_converters(),
            model=ModelConverter,
        )
