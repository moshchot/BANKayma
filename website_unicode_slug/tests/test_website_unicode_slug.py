# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import HttpCase


class TestWebsiteUnicodeSlug(HttpCase):
    def test_page(self):
        """
        Test that pages with unicode paths work
        """
        page_dict = self.env["website"].new_page("röck döts 🤘")
        page = self.env["website.page"].browse(page_dict["page_id"])
        page.write(
            {
                "arch": "<div>hell yeah!</div>",
                "is_published": True,
            }
        )
        result = self.url_open("/röck-döts-🤘")
        self.assertEqual(result.status_code, 200)
        self.assertIn("hell yeah", result.text)

    def test_controller(self):
        """
        Test that the model controller works with unicode slugs
        """
        aland = self.env.ref("base.ax")
        aland_slug = self.env["ir.http"]._slug(aland)
        self.assertEqual(aland_slug, f"%C3%A5land-islands-{aland.id}")
        result = self.url_open(
            url=f"/website/country_infos/{aland_slug}",
            data="{}",
            headers={"content-type": "application/json"},
        )
        self.assertEqual(result.json()["result"]["phone_code"], aland.phone_code)
        result = self.url_open(
            url=f"/website/country_infos/{aland.id}",
            data="{}",
            headers={"content-type": "application/json"},
        )
        self.assertEqual(result.json()["result"]["phone_code"], aland.phone_code)
        result = self.url_open(
            url=f"/website/country_infos/{aland.id}?parameter=value",
            data="{}",
            headers={"content-type": "application/json"},
        )
        self.assertEqual(result.json()["result"]["phone_code"], aland.phone_code)
