# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from collections import namedtuple
from datetime import date

FixedLengthField = namedtuple(
    "OpenformatField", ("code", "length", "name", "type"), defaults=(str,)
)
F = FixedLengthField

# TODO see if we can unify this and sys1k


class OpenformatFile(object):
    encoding = "ISO-8859-8"

    def __init__(self):
        self.records = []

    def append(self, record):
        self.records.append(record)

    def tobytes(self):
        result = "\r\n".join(record.format() for record in self.records)
        return result.encode(self.encoding)


class Record(object):
    def __init__(self, _fields, **_data):
        self._fields = _fields
        self._data = _data

    def _format_field(self, field, data):
        if field.type == int:
            try:
                number = int(str(data or 0).lstrip("0").strip() or 0)
            except ValueError as ex:
                raise ValueError(
                    "Field %(field_name)s must be an integer, got %(value)s"
                    % {
                        "field_name": "%s (%s)" % (field.name, field.code),
                        "value": data,
                    }
                ) from ex
            return ("{:0>%dd}" % field.length).format(number % field.length**10)
        elif field.type == float:
            number = int((data or 0) * 100)
            return ("{:0=+%dd}" % field.length).format(number % field.length**10)
        elif field.type == date:
            data = data or date.min
            return ("{:0>%dd}" % field.length).format(
                data.year * 10000 + data.month * 100 + data.day
            )
        else:
            try:
                str(data or "").encode(OpenformatFile.encoding)
            except ValueError as ex:
                raise ValueError(
                    "Field %(field_name)s contains invalid characters, got %(value)s"
                    % {
                        "field_name": "%s (%s)" % (field.name, field.code),
                        "value": data,
                    }
                ) from ex
            return ("{: <%ds}" % field.length).format(str(data or "")[: field.length])

    def format(self):
        return "".join(
            self._format_field(field, self._data.get(field.name))
            for field in self._fields
        )


class RecordInit(Record):
    def __init__(self, **_data):
        super().__init__(
            (
                F(1000, 4, "code"),
                F(1001, 5, "unused"),
                F(1002, 15, "bkmvdata_count", int),
                F(1003, 9, "vat", int),
                F(1004, 15, "primary_id", int),
                F(1005, 8, "system_constant"),
                F(1006, 8, "software_registration_number", int),
                F(1007, 20, "software_name"),
                F(1008, 20, "software_release"),
                F(1009, 9, "software_serial"),
                F(1010, 20, "software_manufacturer"),
                F(1011, 1, "software_period", int),  # 1=one year, 2=multi
                F(1012, 50, "software_save_path"),
                # 1=no double entry, 2=double entry
                F(1013, 1, "software_accounting_type", int),
                F(1014, 1, "software_balance_required", int),
                F(1015, 9, "company_registry_number", int),
                F(1016, 9, "company_decuction_file_id", int),
                F(1017, 10, "unused_1017"),
                F(1018, 50, "company_name"),
                F(1019, 50, "company_street"),
                F(1020, 10, "company_street_number"),
                F(1021, 30, "company_city"),
                F(1022, 8, "company_zip"),
                F(1023, 4, "year", int),
                F(1024, 8, "date_start", date),
                F(1025, 8, "date_end", date),
                F(1026, 8, "date_export", date),
                F(1027, 4, "time_export", int),
                F(1028, 1, "lang", int),  # 0=he, 1=ar, 2=other
                F(1029, 1, "charset", int),  # 1=iso-8859-8-i, 2=cp862
                F(1030, 20, "compressor_name"),
                F(1032, 3, "currency"),
                F(1034, 1, "branches", int),
                F(1035, 46, "unused_1035"),
            ),
            **_data
        )


class RecordInitSummary(Record):
    def __init__(self, **_data):
        super().__init__(
            (
                F(105, 4, "code"),
                F(1105, 51, "count", int),
            ),
            **_data
        )


class RecordDataOpen(Record):
    def __init__(self, **_data):
        super().__init__(
            (
                F(1100, 4, "code"),
                F(1101, 9, "registered_tax"),
                F(1102, 9, "vat", int),
                F(1103, 15, "primary_id", int),
                F(1104, 8, "system_constant"),
                F(1105, 50, "unused"),
            ),
            **_data
        )
        self._data["code"] = "A100"


class RecordDataClose(Record):
    def __init__(self, **_data):
        super().__init__(
            (
                F(1150, 4, "code"),
                F(1151, 9, "registered_tax"),
                F(1152, 9, "vat", int),
                F(1153, 15, "primary_id", int),
                F(1154, 8, "system_constant"),
                F(1155, 15, "record_count", int),
                F(1156, 50, "unused"),
            ),
            **_data
        )
        self._data["code"] = "Z900"


class RecordDataDocument(Record):
    def __init__(self, **_data):
        super().__init__(
            (
                F(1200, 4, "code"),
                F(1201, 9, "serial", int),
                F(1202, 9, "company_vat", int),
                F(1203, 3, "type", int),
                F(1204, 20, "number"),
                F(1205, 8, "create_date", date),
                F(1206, 4, "create_time", int),
                F(1207, 50, "partner_name"),
                F(1208, 50, "partner_street"),
                F(1209, 10, "partner_street_number"),
                F(1210, 30, "partner_city"),
                F(1211, 8, "partner_zip"),
                F(1212, 30, "partner_country"),
                F(1213, 2, "partner_country_code"),
                F(1214, 15, "partner_phone"),
                F(1215, 9, "partner_vat", int),
                F(1216, 8, "accounting_date", date),
                F(1217, 15, "amount_currency", float),
                F(1218, 3, "amount_currency_code"),
                F(1219, 15, "amount_without_discount", float),
                F(1220, 15, "discount", float),
                F(1221, 15, "amount_with_discount", float),
                F(1222, 15, "amount_tax", float),
                F(1223, 15, "amount_untaxed", float),
                F(1224, 12, "withholding_tax", float),
                F(1225, 15, "partner_id"),
                F(1226, 10, "matching_key"),
                F(1228, 1, "cancelled", int),
                F(1230, 8, "payment_date", date),
                F(1231, 7, "branch_id"),
                F(1233, 9, "user_id"),
                F(1234, 7, "document_id", int),
                F(1235, 13, "unused"),
            ),
            **_data
        )
        self._data["code"] = "C100"
