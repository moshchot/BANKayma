import odoo
import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class TestBankaymaWebsiteSaleFrontend(odoo.tests.HttpCase):
    def test_shop_not_logged_in(self):
        """
        Test shop without login
        """
        self.start_tour("/shop", "bankayma_website_sale_frontend")
        # TODO: assert stuff
