# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import HttpCase, TransactionCase


class SomethingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()

        # TODO Replace this for something useful or delete this method
        self.do_something_before_all_tests()

    def tearDown(self):
        # TODO Replace this for something useful or delete this method
        self.do_something_after_all_tests()

        return super().tearDown()

    def test_something(self):
        """First line of docstring appears in test logs.

        Other lines do not.

        Any method starting with ``test_`` will be tested.
        """


class UICase(HttpCase):
    def test_ui_web(self):
        """Test backend tests."""
        self.browser_js(
            "/web/tests?debug=assets&module=module_name",
            "",
            login="admin",
        )

    def test_ui_website(self):
        """Test frontend tour (v13)."""
        self.start_tour("/shop", "tour_name", login="admin")
