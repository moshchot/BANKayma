# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from collections import namedtuple
from datetime import date

FixedLengthField = namedtuple(
    "FizedLengthField", ("code", "length", "name", "type"), defaults=(str,)
)
F = FixedLengthField


class HashashevetFile:
    encoding = "ISO-8859-8"

    def __init__(self):
        self.records = []

    def append(self, record):
        self.records.append(record)

    def tobytes(self):
        result = "\r\n".join(record.format() for record in self.records)
        return result.encode(self.encoding, errors="replace")


class Record:
    def __init__(self, _fields, **_data):
        self._fields = _fields
        self._field_names = tuple([field.name for field in _fields])
        self._data = _data
        for field in _data:
            if field not in self._field_names:
                raise ValueError(f"Unknown field {field} for {self} given")

    def _format_field(self, field, data):
        if data is None:
            return (" " if field.type is str else "0") * field.length
        if field.type is int:
            try:
                number = int(str(data or 0).lstrip("0").strip() or 0)
            except ValueError as ex:
                raise ValueError(
                    f"Field {field.name} ({field.code}) must be an integer, got {data}"
                ) from ex
            if number < 0:
                raise ValueError(f"Field {field.name} cannot be negative")
            return f"{{:0>{field.length}d}}".format(number % 10**field.length)
        elif field.type is float:
            number = round((data or 0) * 100)
            return f"{{:0={field.length}d}}".format(
                (-1 if number < 0 else 1) * (abs(number) % 10 ** (field.length - 1))
            )
        elif field.type is date:
            data = data or date.min
            return f"{{:0>{field.length}d}}".format(
                data.year * 10000 + data.month * 100 + data.day
            )
        else:
            return f"{{: <{field.length}s}}".format(str(data or "")[: field.length])

    def format(self):
        return "".join(
            self._format_field(field, self._data.get(field.name))
            for field in self._fields
        )

    def __eq__(self, other):
        return self._data == other._data
