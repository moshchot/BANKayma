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
