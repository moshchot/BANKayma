from odoo.tests import Form
from odoo.tests.common import HttpCase


class TestBankaymaWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env.ref("operating_unit.main_operating_unit")
        cls.child = cls.env.ref("operating_unit.b2b_operating_unit")

    def test_project_listing(self):
        response = self.url_open("/projects")
        self.assertIn(self.child.name, response.text)
        self.assertNotIn(self.parent.name, response.text)

    def test_project_page(self):
        response = self.url_open(f"/projects/{self.child.id}")
        self.assertIn(self.child.name, response.text)

    def test_project_embed_page(self):
        response = self.url_open(
            f"/projects/{self.child.id}/embed?"
            "about=1&updates=1&events=1&donation=1&gallery=1&contact=1"
        )
        self.assertIn(self.child.name, response.text)

    def test_project_embed_wizard(self):
        all_options = self.env["bankayma.project.page.embed.code.option"].search([])
        test_option = all_options[0]
        with Form(
            self.env["bankayma.project.page.embed.code"].with_context(
                default_operating_unit_id=self.child.id
            )
        ) as embed_wizard:
            self.assertIn(f"{test_option.value}=", embed_wizard.embed_code)
            embed_wizard.options.remove(test_option.id)
        self.assertNotIn(f"{test_option.value}=", embed_wizard.embed_code)
