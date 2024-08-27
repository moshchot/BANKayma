# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class CompanyCascadeMixin(models.AbstractModel):
    _inherit = "company.cascade.mixin"

    def _company_cascade_get_categories(self):
        return self.env.context.get("company_cascade_catgory_categories") or self.env[
            "res.company.category"
        ].search([])

    def _company_cascade_get_companies(self):
        categories = self._company_cascade_get_categories()
        return (
            super()
            ._company_cascade_get_companies()
            .filtered(lambda x: not x.category_id or x.category_id in categories)
        )

    def _company_cascade_get_children(self):
        categories = self._company_cascade_get_categories()
        return (
            super()
            ._company_cascade_get_children()
            .filtered(
                lambda x: not x.company_id.category_id
                or x.company_id.category_id in categories
            )
        )

    def _company_cascade_get_all(self, company=None):
        categories = self._company_cascade_get_categories()
        return (
            super()
            ._company_cascade_get_all(company=company)
            .filtered(
                lambda x: not x.company_id.category_id
                or x.company_id.category_id in categories
            )
        )
