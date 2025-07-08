from openupgradelib import openupgrade
from openupgradelib.openupgrade_merge_records import merge_records


@openupgrade.migrate()
def migrate(env, version=None):
    # ensure journals on all payment method lines
    env.cr.execute(
        """
        update account_payment_method_line
        set journal_id=method2journal.journal_id from (
            select ap.payment_method_line_id, aj.id journal_id
            from account_payment ap, account_move am, account_journal aj
            where
            ap.move_id=am.id and am.journal_id=aj.id
            and payment_method_line_id in (
                select id from account_payment_method_line where journal_id is null
            )
        ) method2journal
        where method2journal.payment_method_line_id=account_payment_method_line.id
        """
    )
    # merge payment method lines with duplicate payment methods
    env.cr.execute(
        """
        select array_agg(id) ids
        from account_payment_method_line
        group by journal_id, payment_method_id
        having count(payment_method_id)>1
        """
    )
    no_cascade_env = env(
        context=dict(env.context, company_cascade_up=False, company_cascade=False)
    )
    AccountPaymentMethodLine = env["account.payment.method.line"]
    for (ids,) in env.cr.fetchall():
        records = AccountPaymentMethodLine.browse(ids)
        target = records[0]
        merge_records(
            no_cascade_env,
            AccountPaymentMethodLine._name,
            (records - target).ids,
            target.id,
            method="sql",
        )
