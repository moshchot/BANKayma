# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from base64 import b64decode
from collections import namedtuple
from datetime import date, datetime

System1000Field = namedtuple(
    "System1000Field", ("start", "length", "name", "type"), defaults=(str,)
)


class System1000File(object):
    encoding = "ISO-8859-8"
    lines = None
    intro_line = None
    outro_line = None

    def __init__(self, b64_data, data_fields, result_type):
        self.lines = b64decode(b64_data).decode(self.encoding).strip().split("\r\n")
        self.data_fields = data_fields
        self.result_type = result_type

    def __iter__(self):
        for line in self.lines[1:-1]:
            assert line[0] == "B"
            yield self.result_type(
                **{
                    field.name: field.type(
                        line[field.start : field.start + field.length]
                    )
                    for field in self.data_fields
                }
            )

    def _parse_date(self, date_string):
        if date_string == "00000000":
            return date.min
        else:
            return datetime.strptime(date_string, "%Y%m%d").date()


class System1000FileImport(System1000File):
    def __init__(self, b64_data):
        F = System1000Field
        data_fields = [
            F(1, 15, "document_id", str.lstrip),
            F(16, 9, "tax_id_sent"),
            F(25, 9, "vat_id_sent"),
            F(34, 9, "tax_id_received"),
            F(43, 9, "vat_id_received"),
            F(52, 22, "name", str.lstrip),
            F(74, 1, "tax_papers", int),
            F(75, 2, "tax_deduction_income", int),
            F(77, 2, "tax_deduction_agriculture", int),
            F(79, 2, "tax_deduction_insurance", int),
            F(81, 2, "tax_deduction_regulations", int),
            F(83, 2, "tax_deduction_stocks", int),
            F(85, 8, "date_from", self._parse_date),
            F(93, 8, "date_to", self._parse_date),
            F(101, 8, "date_checked", self._parse_date),
            F(109, 3, "deduction_restriction_code"),
            F(112, 9, "deduction_id"),
            F(121, 10, "max_amount"),
            F(131, 9, "employer_tax_id"),
        ]
        super().__init__(
            b64_data,
            data_fields,
            namedtuple(
                "System1000FileImportData",
                [data_field.name for data_field in data_fields],
            ),
        )


class System1000FileImportInvalid(System1000File):
    def __init__(self, b64_data):
        F = System1000Field
        data_fields = [
            F(1, 15, "document_id", str.lstrip),
            F(16, 9, "tax_id_sent"),
            F(25, 9, "vat_id_sent"),
            F(34, 2, "error_code", int),
            F(36, 50, "error_comment"),
        ]
        super().__init__(
            b64_data,
            data_fields,
            namedtuple(
                "System1000FileImportInvalidData",
                [data_field.name for data_field in data_fields],
            ),
        )
