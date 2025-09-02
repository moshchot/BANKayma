# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from odoo.addons.http_routing.models import ir_http


class ModelConverter(ir_http.ModelConverter):
    def to_url(self, value):
        # sudo the record we got to allow model(something) in routes and sudoing
        # afterwards
        return super().to_url(value.sudo())


class IrHttp(models.AbstractModel):
    _inherit = ["ir.http"]

    @classmethod
    def _get_converters(cls):
        return dict(
            super(IrHttp, cls)._get_converters(),
            model=ModelConverter,
        )
