# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from urllib.parse import urljoin

import requests

from odoo import api, exceptions, fields, models


class SumitAccount(models.Model):
    _name = "sumit.account"
    _rec_name = "company_code"
    _order = "sequence"

    api_url = "https://api.sumit.co.il"
    timeout = 60

    sequence = fields.Integer()
    company_code = fields.Char("CompanyId", required=True)
    key = fields.Char("APIKey", required=True, groups="base.group_system")
    company_id = fields.Many2one("res.company")

    @api.model
    def _get_account(self):
        return self.sudo().search(
            [
                ("company_id", "in", (False, self.env.company.id)),
            ],
            limit=1,
        )

    @api.model
    def _request(self, endpoint, payload):
        account = self._get_account()
        data = dict(
            payload,
            Credentials={
                "CompanyID": account.company_code,
                "APIKey": account.key,
            },
        )
        result = requests.post(
            urljoin(self.api_url, endpoint),
            json=data,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/plain",
            },
            allow_redirects=False,
        ).json()
        if result.get("Status"):
            # TODO log error
            raise exceptions.UserError(
                result.get("UserErrorMessage") or result.get("TechnicalErrorDetails")
            )
        return result.get("Data", {})

    @api.model
    def sumit_language(self, lang):
        # TODO: add remaining langs
        return "0" if lang == "he_IL" else "1"

    @api.model
    def sumit_currency(self, currency):
        # TODO: add remaining currencies
        return (
            "0"
            if currency.name == "ILS"
            else "1"
            if currency.name == "USD"
            else "2"
            if currency.name == "EUR"
            else None
        )
