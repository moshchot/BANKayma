from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    env.cr.execute(
        """
        update account_move_line
        set account_id=account_account.id
        from account_account, account_move, account_fiscal_position
        where
        product_id is not null and
        parent_state = 'posted' and
        account_fiscal_position.code in ('4', '5') and
        account_account.code='101440' and
        account_account.company_id=account_move_line.company_id and
        move_id=account_move.id and
        account_move.fiscal_position_id=account_fiscal_position.id
        """
    )
    env["account.account"].search([])._compute_current_balance()
