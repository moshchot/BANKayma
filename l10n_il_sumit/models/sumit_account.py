# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


import enum
import logging
from urllib.parse import urljoin

import requests

from odoo import api, exceptions, fields, models

_logger = logging.getLogger(__name__)


SUMIT_DOCUMENT_TYPE_SELECTION = [
    ("0", "Invoice"),
    ("1", "Invoice And Receipt"),
    ("2", "Receipt"),
    ("3", "Proforma Invoice"),
    ("4", "Donation Receipt"),
    ("5", "Credit Invoice"),
    ("6", "Credit Invoice And Receipt"),
    ("7", "Credit Receipt"),
    ("8", "Order"),
    ("9", "Delivery Note"),
    ("10", "Goods Return Note"),
    ("11", "Purchasing Order"),
    ("12", "Price Quotation"),
    ("13", "Payment Request"),
    ("14", "Credit Donation Receipt"),
    ("15", "Expense Invoice Receipt"),
    ("16", "Expense Invoice"),
    ("17", "Expense Receipt"),
    ("18", "Expense Request"),
    ("19", "Credit Expense Invoice Receipt"),
    ("20", "Credit Expense Invoice"),
    ("21", "Credit Expense Receipt"),
]


# pylint: disable=class-camelcase
class SUMIT_PAYMENT_TYPE(enum.StrEnum):
    AUTOMATIC = "0"
    GENERAL = "1"
    CASH = "2"
    BANK_TRANSFER = "3"
    CHEQUE = "4"
    CREDIT_CARD = "5"
    TYPE_DIGITAL = "6"
    TAX_WITHHOLDING = "7"
    OTHER = "8"


SUMIT_PAYMENT_TYPE_SELECTION = [
    (SUMIT_PAYMENT_TYPE.AUTOMATIC, "Automatic"),
    (SUMIT_PAYMENT_TYPE.GENERAL, "General"),
    (SUMIT_PAYMENT_TYPE.CASH, "Cash"),
    (SUMIT_PAYMENT_TYPE.BANK_TRANSFER, "Bank Transfer"),
    (SUMIT_PAYMENT_TYPE.CHEQUE, "Cheque"),
    (SUMIT_PAYMENT_TYPE.CREDIT_CARD, "Credit Card"),
    (SUMIT_PAYMENT_TYPE.TYPE_DIGITAL, "Digital"),
    (SUMIT_PAYMENT_TYPE.TAX_WITHHOLDING, "Tax Withholding"),
    (SUMIT_PAYMENT_TYPE.OTHER, "Other"),
]


class SumitAccount(models.Model):
    _name = "sumit.account"
    _rec_name = "company_code"
    _order = "sequence"
    _description = "Sumit account"

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
        _logger.debug("sending payload: %s", payload)
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
        _logger.debug("result %s", result)
        if result.get("Status") or result.get("ErrorMessage"):
            _logger.error(result)
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
