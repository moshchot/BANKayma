import ast

from lxml import etree
from openupgradelib.openupgrade import migrate, rename_fields, update_module_names


def update_context_or_domain(  # noqa: C901
    context_or_domain, update_name_func=None, update_value_func=None
):
    """
    Given a string containing a domain, this function
    returns a text representation of it modified as executed by the
    update_* functions passed.

    :param domain: an Odoo domain like "[('some_field', '=', value)]"
    :param update_name_func: function being passed a field name as string, returning a
    replacement string.

    Example:

    With::

        def rename_company_id(name):
            if name == 'company_id':
                return 'company_id2'
            return name

    calling::

        update_domain("[('company_id', '=', 42), ('other_field', '=', value)]",
        update_name_func=rename_company_id)

    returns::

        "[('company_id2', '=', 42), ('other_field', '=', value)]"

    :param update_value_func: function being passed a domain field name as string, and a
    value as string, int, list or ast.Expression if the right hand side of a domain leaf
    cannot be parsed as one of the former. Return one of the aformentioned types to
    replace the right hand side of the domain leaf.

    Example:

    With::

        def change_company_id(name, value):
            if name == 'company_id':
                if isinstance(value, int) and value == 42:
                    return 43
                elif isinstance(value, (list, tuple)) and 42 in value:
                    return [val if val != 42 else 43 for val in value]
            return value

    calling::

        update_domain(
            "[('company_id', '=', 42), ('company_id', 'in', [41, 42]), "
            "('other_field', '=', value)]",
            update_value_func=change_company_id
        )

    returns::

        "[('company_id', '=', 43), ('company_id', 'in', (41, 43)), "
        "('other_field', '=', value)]"
    """

    class Transformer(ast.NodeTransformer):
        def visit_Dict(self, node):
            keys, values = [], []
            for key, value in zip(node.keys, node.values, strict=False):
                new_key = None
                if update_name_func:
                    new_key = update_name_func(self._get_literal_value_or_ast(key))

                keys.append(self._get_ast_for_value(new_key or key))

                new_value = None
                if update_value_func:
                    new_value = update_value_func(
                        self._get_literal_value_or_ast(key),
                        self._get_literal_value_or_ast(value),
                    )

                values.append(self._get_ast_for_value(new_value or value))

            node.keys = keys
            node.values = values

            return node

        def visit_List(self, node):
            for element in node.elts:
                if not isinstance(element, ast.List | ast.Tuple):
                    continue

                left = element.elts[0]
                if not isinstance(left, ast.Constant) or len(element.elts) != 3:
                    continue

                if update_name_func:
                    new_left = update_name_func(left.value)
                    element.elts[0] = self._get_ast_for_value(new_left or left)

                if update_value_func:
                    new_right = update_value_func(
                        left.value, self._get_literal_value_or_ast(element.elts[2])
                    )
                    element.elts[2] = self._get_ast_for_value(
                        new_right or element.elts[2]
                    )

            return node

        def _get_literal_value_or_ast(self, node):
            try:
                return ast.literal_eval(node)
            except Exception:
                return node

        def _get_ast_for_value(self, value):
            if isinstance(value, int | str | float):
                return ast.Constant(value)
            elif isinstance(value, list | tuple):
                return ast.Tuple([self._get_ast_for_value(val) for val in value])
            elif isinstance(value, dict):
                return ast.Dict(
                    [self._get_ast_for_value(val) for val in value.keys()],
                    [self._get_ast_for_value(val) for val in value.values()],
                )
            return value

    expr = ast.parse(context_or_domain, mode="eval")
    return ast.unparse(Transformer().visit(expr))


@migrate()
def migrate(env, version=None):  # noqa: C901
    # transistion company categories and tags to operating unit categories and tags

    env.cr.execute("ALTER TABLE res_company_category RENAME TO operating_unit_category")
    env.cr.execute("ALTER TABLE res_company_tag RENAME TO operating_unit_tag")
    env.cr.execute("ALTER TABLE operating_unit ADD COLUMN category_id int")
    env.cr.execute(
        """
        UPDATE
        operating_unit ou
        SET
        category_id=rc.category_id
        FROM res_company_bk_pre_v18 rc
        WHERE
        rc.id=ou.bankayma_from_company_id
        """
    )
    env.cr.execute(
        """
        UPDATE
        res_company
        SET
        category_id=NULL
        """
    )
    update_module_names(
        env.cr,
        [
            ("bankayma_migrate_v18", "bankayma_base"),
            ("web_select_all_companies", "bankayma_base"),
            ("mass_mailing_multi_company", "bankayma_base"),
            ("email_template_qweb", "bankayma_base"),
            ("res_company_tag", "bankayma_base"),
        ],
        merge_modules=True,
    )

    # in filters:
    # change restrictions on company_id to operating_unit_id{,s}

    env.cr.execute("select bankayma_from_company_id, id from operating_unit")
    comp_id2ou_id = dict(env.cr.fetchall())

    def rename_company_id(name):
        if name == "company_id":
            return "operating_unit_id"
        return name

    def rename_company_id_ids(name):
        if name == "company_id":
            return "operating_unit_ids"
        return name

    def change_company_id(name, value):
        if name == "company_id":
            if isinstance(value, int):
                return comp_id2ou_id.get(value, value)
            elif isinstance(value, list | tuple):
                return [comp_id2ou_id.get(val, val) for val in value]
        if name == "group_by":
            if isinstance(value, list | tuple):
                return [
                    ("operating_unit_id" if val == "company_id" else val)
                    for val in value
                ]
        return value

    for ir_filter in env["ir.filters"].with_context(active_test=False).search([]):
        if ir_filter.model_id not in env:
            continue
        if "operating_unit_id" in env[ir_filter.model_id]._fields:
            update_name_func = rename_company_id
        else:
            update_name_func = rename_company_id_ids
        ir_filter.domain = update_context_or_domain(
            ir_filter.domain,
            update_name_func=update_name_func,
            update_value_func=change_company_id,
        )
        ir_filter.context = update_context_or_domain(
            ir_filter.context,
            update_value_func=change_company_id,
        )

    # in dashboards:
    # change [('plan_id', 'like', ...)] to [('auto_account_id.plan_id', ...)
    # remove grouping by account_id

    def rename_plan_id(name):
        if name == "plan_id":
            return "auto_account_id.plan_id"
        return name

    def change_groupby(name, value):
        if name == "group_by":
            if isinstance(value, list) and "account_id" in value:
                return [val for val in value if val != "account_id"]
        return value

    for custom_view in env["ir.ui.view.custom"].search([]):
        arch = etree.fromstring(custom_view.arch)
        for action in arch.xpath("//board//action"):
            if action.attrib.get("context"):
                try:
                    action.attrib["context"] = update_context_or_domain(
                        action.attrib["context"], update_value_func=change_groupby
                    )
                except Exception:  # pylint: disable=except-pass
                    pass
            if action.attrib.get("domain"):
                try:
                    action.attrib["domain"] = update_context_or_domain(
                        action.attrib["domain"], update_name_func=rename_plan_id
                    )
                except Exception:  # pylint: disable=except-pass
                    pass
        custom_view.arch = etree.tostring(arch)

    # revert multilang fields
    for field_name in ("name", "city", "function", "street", "street2"):
        env.cr.execute(
            f"""
            ALTER TABLE res_partner
            RENAME COLUMN {field_name} TO {field_name}_unilanguage;
            ALTER TABLE res_partner
            RENAME COLUMN {field_name}_multilanguage TO {field_name};
            """
        )

    # rename misc fields
    rename_fields(
        env,
        [
            (
                "operating.unit.category",
                "operating_unit_category",
                "show_in_company_selector",
                "show_in_ou_selector",
            )
        ],
    )
