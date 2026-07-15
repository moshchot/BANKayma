# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
import re
from urllib.parse import quote

import werkzeug

from odoo import models
from odoo.http import request

from odoo.addons.website.models import ir_http


class ModelConverter(ir_http.ModelConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = r"(?:.*-)?\d+(?=$|\/|#|\?)"

    def to_python(self, value):
        _dummy, _id = self.unslug(value)
        if not _id:
            raise werkzeug.routing.ValidationError()
        return super().to_python(str(_id))


class IrHttp(models.AbstractModel):
    _inherit = ["ir.http"]

    @classmethod
    def _slugify_one(cls, value: str, max_length: int = 0) -> str:
        result = ""
        value = re.sub(r"[-_/#?\s]+", "-", value.lower())
        quoted = map(quote, value)
        for quoted_char in quoted:
            if not max_length or len(result) + len(quoted_char) <= max_length:
                result += quoted_char
            else:
                break
        return result

    @classmethod
    def _unslug(cls, value: str) -> tuple[str | None, int] | tuple[None, None]:
        slug = ""
        _id = ""
        if not value:
            return None, None
        value = value.rstrip("/?#")
        for i in range(len(value) - 1, -1, -1):
            if value[i].isdigit():
                _id = value[i] + _id
            else:
                if value[i] == "-":
                    slug = value[:i]
                else:
                    slug, _id = None, None
                break
        return slug, int(_id) if _id else _id

    @classmethod
    def _get_converters(cls) -> dict[str, type]:
        return dict(
            super()._get_converters(),
            model=ModelConverter,
        )

    @classmethod
    def _serve_fallback(cls):
        request.httprequest.path = "/" + cls._slugify(
            request.httprequest.path, path=True
        )
        return super()._serve_fallback()
