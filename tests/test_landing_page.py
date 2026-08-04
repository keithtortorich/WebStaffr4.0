"""Smoke tests for the public landing page (GET /, webstaffr/landing_router.py).

This page had no test coverage before this file -- added alongside the
2026-07-29 visual restyle so a future edit can't silently reintroduce a
debunked statistic or break the page. Not a full content/accessibility
suite, just the guardrails this session's change depends on.
"""

from __future__ import annotations

import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from webstaffr.app import create_app


class LandingPageTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        app = create_app(db_path=self.db_path)
        self._client_ctx = TestClient(app)
        self.client = self._client_ctx.__enter__()

    def tearDown(self):
        self._client_ctx.__exit__(None, None, None)
        os.remove(self.db_path)

    def test_landing_page_renders(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("NetBuild.Pro", resp.text)

    def test_contact_phone_present(self):
        resp = self.client.get("/")
        self.assertIn("(888) 302-8368", resp.text)
        self.assertIn("tel:+18883028368", resp.text)

    def test_no_unrendered_template_tokens(self):
        """Every __TOKEN__ placeholder in _LANDING_PAGE_HTML must be
        substituted -- a leftover token means a substitution was added to
        the HTML but not to _render_landing_page()'s .replace() chain."""
        resp = self.client.get("/")
        self.assertNotIn("__CONTACT_", resp.text)
        self.assertNotIn("__ICON_", resp.text)

    def test_no_debunked_response_rate_stat(self):
        """The '78% of homeowners hire whoever responds first' claim was
        already found, flagged, and removed elsewhere in this repo
        (sales-crm.html, the real website copy -- see TASKS.md 2026-07-27)
        after failing independent verification twice. It had drifted back
        in here; this pins it removed."""
        resp = self.client.get("/")
        self.assertNotIn("78%", resp.text)
        self.assertNotIn("85%", resp.text)

    def test_landing_calls_to_action_open_working_intake(self):
        landing = self.client.get("/")
        self.assertIn('href="/start"', landing.text)

        intake = self.client.get("/start")
        self.assertEqual(intake.status_code, 200)
        self.assertIn('id="intake-form"', intake.text)
        self.assertIn("Create My 24/7 Receptionist", intake.text)
        self.assertIn("fetch('/intake'", intake.text)

    def test_intake_exposes_tradesman_mvp_choices(self):
        resp = self.client.get("/start")
        for expected in (
            "Plumber", "Electrician", "HVAC", "Pest Control",
            "Professional", "Enterprise", "Text my cell", "Route to GHL",
            "Founder only", "Team",
        ):
            self.assertIn(expected, resp.text)

    def test_demo_redirect_known_trade(self):
        resp = self.client.get("/demos/plumbing", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/sites/demo-plumbing/web", resp.headers["location"])

    def test_demo_redirect_unknown_trade(self):
        resp = self.client.get("/demos/not-a-real-trade")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("error", resp.json())


if __name__ == "__main__":
    unittest.main()
