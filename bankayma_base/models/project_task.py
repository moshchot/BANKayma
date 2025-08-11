# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .. import fields as bankayma_base_fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    partner_name = bankayma_base_fields.TranslatedComputedChar()
    partner_company_name = bankayma_base_fields.TranslatedComputedChar()
