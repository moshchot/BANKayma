# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class IrModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def _load_module_terms(self, modules, langs, overwrite=False):
        """Always overwrite translations"""
        return super()._load_module_terms(modules, langs, overwrite=True)
