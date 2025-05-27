# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools


class AccountPaymentTerm(models.AbstractModel):
    _inherit = "account.payment.term"

    _order = "fixed_date asc, sequence, id"

    fixed_date = fields.Date(
        string="Date", help="Set a fixed date instead of relative terms below"
    )

    def name_get(self):
        return [
            (
                _id,
                _name
                if not self.browse(_id).fixed_date
                else self.browse(_id).fixed_date.strftime("%d/%m/%Y"),
            )
            for _id, _name in super().name_get()
        ]

    @api.onchange("fixed_date")
    def _onchange_fixed_date(self):
        self.name = (
            tools.format_date(self.env, self.fixed_date)
            if self.fixed_date
            else self.name
        )

    def _compute_terms(
        self,
        date_ref,
        currency,
        company,
        tax_amount,
        tax_amount_currency,
        sign,
        untaxed_amount,
        untaxed_amount_currency,
        cash_rounding=None,
    ):
        self.ensure_one()
        if not self.fixed_date:
            return super()._compute_terms(
                date_ref,
                currency,
                company,
                tax_amount,
                tax_amount_currency,
                sign,
                untaxed_amount,
                untaxed_amount_currency,
                cash_rounding=cash_rounding,
            )
        return [
            {
                "company_amount": company.currency_id.round(
                    tax_amount + untaxed_amount
                ),
                "foreign_amount": company.currency_id.round(
                    tax_amount_currency + untaxed_amount_currency
                ),
                "has_discount": 0.0,
                "date": self.fixed_date,
                "discount_date": None,
                "discount_amount_currency": 0.0,
                "discount_balance": 0.0,
                "discount_percentage": 0.0,
            }
        ]
