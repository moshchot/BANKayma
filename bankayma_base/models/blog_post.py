# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from .. import fields as bankayma_base_fields


class BlogPost(models.Model):
    _inherit = ["blog.post"]

    author_name = bankayma_base_fields.TranslatedComputedChar()
    operating_unit_id = fields.Many2one("operating.unit")
