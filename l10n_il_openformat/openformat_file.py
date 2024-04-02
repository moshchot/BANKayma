# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from base64 import b64decode
from collections import namedtuple
from datetime import date, datetime

FixedLengthField = namedtuple(
    "OpenformatField", ("length", "name", "type"), defaults=(str,)
)
F = FixedLengthField

# TODO see if we can unify this and sys1k

class OpenformatFile(object):
    encoding = "ISO-8859-8"

    def __init__(self):
        self.lines = []

    def __add__(self, line):
        self.lines.append(line)

RecordTypeInit = namedtuple(
    'RecordTypeInit', (
        F(4, 'code'),
        F(5, 'unused'),
        F(15, 'bkmvdata_count', int),
        F(9, 'authorized_dealer_number', int),
        F(15, 'primary_id', int),
        F(8, 'system_constant'),
        F(8, 'software_registration_number', int),
        F(20, 'software_name'),
        F(20, 'software_release'),
        F(9, 'software_serial'),
        F(20, 'software_manufacturer'),
        F(1, 'software_period', int), # 1=one year, 2=multi
        F(50, 'software_save_path'),
        F(1, 'software_accounting_type', int), # 1=no double entry, 2=double entry
        F(1, 'software_balance_required', int),
        F(9, 'company_registry_number', int),
        F(9, 'company_decuction_file_id', int),
        F(10, 'unused_1017'),
        F(50, 'company_name'),
        F(50, 'company_street'),
        F(10, 'company_street_number'),
        F(30, 'company_city'),
        F(8, 'company_zip'),
        F(4, 'year', int),
        F(8, 'date_start', int),
        F(8, 'date_end', int),
        F(8, 'date_export', int),
        F(4, 'time_export', int),
        F(1, 'lang', int), # 0=he, 1=ar, 2=other
        F(1, 'charset', int), # 1=iso-8859-8-i, 2=cp862
        F(20, 'compressor_name'),
        F(3, 'currency'),
        F(1, 'branches', int),
        F(46, 'unused_1034'),
    )
)
