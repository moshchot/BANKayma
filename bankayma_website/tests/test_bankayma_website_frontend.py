import odoo
import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class TestBankaymaWebsiteFrontend(odoo.tests.HttpCase):
    def test_news(self):
        self.start_tour("/news", "bankayma_website_frontend_news")

    def test_event(self):
        self.start_tour("/event", "bankayma_website_frontend_event")
