import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from webstaffr.app import create_app

# Mirrors CLAUDE.md's never-leak list and test_site_data.py's
# _INTERNAL_FIELDS -- every one of these must never appear, verbatim, in
# any rendered HTML page, exactly as the JSON endpoint already guarantees
# for the API response.
_NEVER_LEAK_VALUES = {
    "lead_routing": "Text Maria at 602-555-0101, replies within 1 hour.",
    "approver": "Maria Lopez",
    "competitors": "Ace Plumbing, Best Plumbing Co",
    "license_number": "ROC 999999",
}

_FORBIDDEN_COPY = ("AI", "—")  # brand governance: no "AI", no em-dash


def _valid_payload(**overrides):
    payload = {
        "biz_name": "Desert Pro Plumbing",
        "phone": "602-555-0100",
        "email": "owner@example.com",
        "industry": "Plumber",
        "service_area": "Phoenix, AZ",
        "tagline": "Fast, honest plumbing.",
        "differentiator": "We show up on time, every time.",
        "services": ["Leak Repair", "Drain Cleaning"],
        "license_number": _NEVER_LEAK_VALUES["license_number"],
        "plan": "growth",
        "lead_routing": _NEVER_LEAK_VALUES["lead_routing"],
        "approver": _NEVER_LEAK_VALUES["approver"],
        "competitors": _NEVER_LEAK_VALUES["competitors"],
    }
    payload.update(overrides)
    return payload


class SiteRenderTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        app = create_app(db_path=self.db_path)
        self._client_ctx = TestClient(app)
        self.client = self._client_ctx.__enter__()

    def tearDown(self):
        self._client_ctx.__exit__(None, None, None)
        os.remove(self.db_path)

    def _make_tenant(self, **overrides) -> str:
        resp = self.client.post("/intake", json=_valid_payload(**overrides))
        self.assertEqual(resp.status_code, 200, resp.text)
        return resp.json()["tenant_id"]


class TestRenderedPagesRoundTrip(SiteRenderTestCase):
    def test_home_page_renders_business_content(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        self.assertIn("Desert Pro Plumbing", resp.text)
        self.assertIn("Fast, honest plumbing.", resp.text)
        self.assertIn("Leak Repair", resp.text)
        self.assertIn("Drain Cleaning", resp.text)

    def test_service_page_renders_and_links_back_to_other_services(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/services/leak-repair")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Leak Repair", resp.text)
        self.assertIn("Drain Cleaning", resp.text)  # cross-linked as "other services"

    def test_unknown_service_slug_returns_404(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/services/does-not-exist")
        self.assertEqual(resp.status_code, 404)

    def test_about_page_renders(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/about")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Desert Pro Plumbing", resp.text)

    def test_contact_page_renders_phone_and_email(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/contact")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("602-555-0100", resp.text)
        self.assertIn("owner@example.com", resp.text)

    def test_sitemap_lists_every_page(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/xml", resp.headers["content-type"])
        self.assertIn(f"/sites/{tenant_id}/web</loc>", resp.text)
        self.assertIn(f"/sites/{tenant_id}/web/about</loc>", resp.text)
        self.assertIn(f"/sites/{tenant_id}/web/contact</loc>", resp.text)
        self.assertIn(f"/sites/{tenant_id}/web/services/leak-repair</loc>", resp.text)
        # No rating/review data submitted -- reviews page must not be listed.
        self.assertNotIn("/reviews</loc>", resp.text)

    def test_robots_txt_points_at_sitemap(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f"/sites/{tenant_id}/web/sitemap.xml", resp.text)

    def test_static_assets_serve(self):
        css = self.client.get("/static/site.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn("text/css", css.headers["content-type"])

        widget = self.client.get("/static/angel-widget.js")
        self.assertEqual(widget.status_code, 200)
        self.assertIn("javascript", widget.headers["content-type"])

    def test_widget_embed_present_on_rendered_page(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web")
        self.assertIn('src="/static/angel-widget.js"', resp.text)
        self.assertIn(f'data-tenant-id="{tenant_id}"', resp.text)


class TestReviewsPageGating(SiteRenderTestCase):
    def test_reviews_page_404s_when_no_rating_on_file(self):
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web/reviews")
        self.assertEqual(resp.status_code, 404)

    def test_reviews_page_renders_when_real_rating_present(self):
        tenant_id = self._make_tenant(
            rating_value=4.9, review_count=214, testimonials="They saved our weekend."
        )
        resp = self.client.get(f"/sites/{tenant_id}/web/reviews")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("4.9", resp.text)
        self.assertIn("214", resp.text)
        self.assertIn("They saved our weekend.", resp.text)

    def test_reviews_page_listed_in_sitemap_only_when_present(self):
        tenant_id = self._make_tenant(rating_value=4.9, review_count=214)
        resp = self.client.get(f"/sites/{tenant_id}/web/sitemap.xml")
        self.assertIn(f"/sites/{tenant_id}/web/reviews</loc>", resp.text)


class TestNoFabrication(SiteRenderTestCase):
    def test_no_review_schema_without_real_review_data(self):
        """The SEO blueprint's Review schema example hardcodes a fabricated
        rating/review as boilerplate (flagged in
        docs/SITE_WEAVER_SEO_BLUEPRINT.md) -- this asserts the renderer
        never emits an aggregateRating block for a tenant with no real
        rating/review data on file."""
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web")
        self.assertNotIn("aggregateRating", resp.text)
        self.assertNotIn("Mike R.", resp.text)  # the blueprint's example author

    def test_aggregate_rating_schema_present_only_with_real_data(self):
        tenant_id = self._make_tenant(rating_value=4.9, review_count=214)
        resp = self.client.get(f"/sites/{tenant_id}/web")
        self.assertIn("aggregateRating", resp.text)
        self.assertIn("4.9", resp.text)

    def test_no_faq_schema_ever(self):
        """No FAQPage schema anywhere -- intake collects no structured
        Q&A content to back one, so it's never generated (see
        build_page_context's docstring)."""
        tenant_id = self._make_tenant()
        resp = self.client.get(f"/sites/{tenant_id}/web")
        self.assertNotIn("FAQPage", resp.text)

    def test_no_forbidden_brand_copy_in_rendered_output(self):
        """Governance Manual rule (default per CLAUDE.md until reconciled):
        no em-dashes, no 'AI' language, anywhere in NetBuild.Pro-authored
        copy. This checks the template-authored strings only by using a
        payload with no em-dash/'AI' substrings of its own, so a failure
        here means the *template*, not the input, introduced one."""
        tenant_id = self._make_tenant()
        for path in ("/web", "/web/about", "/web/contact"):
            resp = self.client.get(f"/sites/{tenant_id}{path}")
            for forbidden in _FORBIDDEN_COPY:
                self.assertNotIn(
                    forbidden, resp.text, f"{forbidden!r} found in {path}"
                )


class TestNeverLeak(SiteRenderTestCase):
    def test_internal_fields_never_appear_in_rendered_html(self):
        tenant_id = self._make_tenant()
        for path in (
            "/web",
            "/web/about",
            "/web/contact",
            "/web/services/leak-repair",
            "/web/sitemap.xml",
            "/web/robots.txt",
        ):
            resp = self.client.get(f"/sites/{tenant_id}{path}")
            for field_name, value in _NEVER_LEAK_VALUES.items():
                self.assertNotIn(
                    value, resp.text, f"{field_name}'s value leaked into {path}"
                )


class TestTenantIsolation(SiteRenderTestCase):
    def test_one_tenants_rendered_page_never_contains_another_tenants_data(self):
        tenant_a = self._make_tenant(biz_name="Alpha Plumbing", phone="602-555-0001")
        tenant_b = self._make_tenant(biz_name="Beta Electric", phone="602-555-0002")

        page_a = self.client.get(f"/sites/{tenant_a}/web").text
        page_b = self.client.get(f"/sites/{tenant_b}/web").text

        self.assertIn("Alpha Plumbing", page_a)
        self.assertNotIn("Beta Electric", page_a)
        self.assertNotIn("602-555-0002", page_a)

        self.assertIn("Beta Electric", page_b)
        self.assertNotIn("Alpha Plumbing", page_b)
        self.assertNotIn("602-555-0001", page_b)


class TestUnknownTenant(SiteRenderTestCase):
    def test_unknown_tenant_returns_404_on_every_rendered_route(self):
        for path in (
            "/web",
            "/web/about",
            "/web/contact",
            "/web/reviews",
            "/web/services/anything",
            "/web/sitemap.xml",
            "/web/robots.txt",
        ):
            resp = self.client.get(f"/sites/no_such_tenant_at_all{path}")
            self.assertEqual(resp.status_code, 404, path)

    def test_invalid_tenant_id_returns_404_not_500(self):
        resp = self.client.get("/sites/bad id with spaces/web")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
