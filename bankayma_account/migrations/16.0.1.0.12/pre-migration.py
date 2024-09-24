def migrate(cr, version=None):
    cr.execute("delete from account_payment_method_line where journal_id is null")
