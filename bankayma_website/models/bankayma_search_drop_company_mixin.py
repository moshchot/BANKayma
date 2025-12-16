from odoo import api, models
from odoo.osv import expression


class BankaymaSearchDropCompanyMixin(models.AbstractModel):
    _name = "bankayma.search.drop.company.mixin"
    _description = "Mixin to remove company filters in website snippet"

    @api.model
    def _where_calc(self, domain, active_test=True):
        if self.env.context.get("bankayma_search_drop_company"):
            domain = [
                leaf
                if (not expression.is_leaf(leaf) or leaf[0] != "company_id")
                else expression.TRUE_LEAF
                for leaf in domain
            ]
        return super()._where_calc(domain, active_test=active_test)
