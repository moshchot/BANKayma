# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .sumit_account import SUMIT_PAYMENT_TYPE


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sumit_document_url = fields.Char("Sumit document", readonly=True)

    def _to_sumit_vals(self):
        self.ensure_one()
        payment_method = self.payment_method_line_id.payment_method_id
        sumit_type = payment_method.sumit_type
        result = {
            "Amount": self.amount,
            "DocumentCurrency_Amount": None,
            "Type": sumit_type,
            "Details_General": None,
            "Details_Cash": None,
            "Details_BankTransfer": None,
            "Details_Cheque": None,
            "Details_CreditCard": None,
            "Details_Other": None,
            "Details_Digital": None,
            "Details_TaxWithholding": None,
        }

        if sumit_type == SUMIT_PAYMENT_TYPE.AUTOMATIC:
            pass
        elif sumit_type == SUMIT_PAYMENT_TYPE.GENERAL:
            result["Details_General"] = {}
        elif sumit_type == SUMIT_PAYMENT_TYPE.CASH:
            result["Details_Cash"] = {}
        elif sumit_type == SUMIT_PAYMENT_TYPE.BANK_TRANSFER:
            result["Details_BankTransfer"] = {
                "BankNumber": None,
                "BranchNumber": None,
                "AccountNumber": None,
                "Reference": None,
                "DueDate": None,
            }
        elif sumit_type == SUMIT_PAYMENT_TYPE.CHEQUE:
            result["Details_Cheque"] = {
                "BankNumber": None,
                "BranchNumber": None,
                "AccountNumber": None,
                "ChequeNumber": None,
                "DueDate": None,
            }
        elif sumit_type == SUMIT_PAYMENT_TYPE.CREDIT_CARD:
            result["Details_CreditCard"] = {
                "CardBrand": None,
                "Last4Digits": None,
                "FirstPayment": None,
                "EachPayment": None,
                "Payments": None,
            }
        elif sumit_type == SUMIT_PAYMENT_TYPE.DIGITAL:
            result["Details_Digital"] = {
                "Type": payment_method.code,
                "Description": payment_method.name,
            }
        elif sumit_type == SUMIT_PAYMENT_TYPE.TAX_WITHHOLDING:
            result["Details_TaxWithholding"] = {}
        else:
            result["Type"] = SUMIT_PAYMENT_TYPE.OTHER
            result["Details_Other"] = {
                "Type": payment_method.code,
                "Description": payment_method.name,
                "DueDate": self.date.isoformat(),
            }

        return result
