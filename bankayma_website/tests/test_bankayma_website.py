from odoo.tests.common import HttpCase


class TestBankaymaWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent_company = cls.env.ref("base.main_company")
        cls.child_company = cls.env.ref("bankayma_base.child_comp1")

    def test_project_listing(self):
        response = self.url_open("/projects")
        self.assertIn(self.child_company.name, response.text)
        self.assertNotIn(self.parent_company.name, response.text)

    def test_project_page(self):
        response = self.url_open("/projects/%s" % self.child_company.id)
        self.assertIn(self.child_company.name, response.text)
