def migrate(cr, version=None):
    cr.execute("alter table account_analytic_line drop column bankayma_expense")
