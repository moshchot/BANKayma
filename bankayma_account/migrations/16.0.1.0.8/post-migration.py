from psycopg2.extensions import AsIs


def migrate(cr, version=None):
    for table, column in (
        ("res_partner", "vat"),
        ("res_partner_bank", "acc_number"),
        ("res_partner_bank", "branch_code"),
    ):
        cr.execute(
            "update %(table)s set "
            "%(column)s=regexp_replace(%(column)s, '[^0-9]', '', 'g') "
            "where %(column)s ~ '[^0-9]+'",
            {"table": AsIs(table), "column": AsIs(column)},
        )
