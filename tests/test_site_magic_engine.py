"""Tests for site_magic_engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from webstaffr.intake import IntakeSubmission
from webstaffr.site_magic_engine import SiteGenerationResult, generate_site_for_submission


def _minimal_submission(tmp_path: Path) -> IntakeSubmission:
    return IntakeSubmission(
        tenant_id="test_tenant",
        biz_name="Test Biz",
        phone="555-0000",
        email="test@example.com",
        industry="Other",
        service_area="Nowhere",
        tagline="Tagline",
        differentiator="Differentiator",
        services=["Service A"],
        license_number="LIC-1",
        plan="essentials",
        lead_routing="office",
        approver="owner",
    )


def test_generate_site_writes_pages(tmp_path: Path):
    submission = _minimal_submission(tmp_path)
    result = generate_site_for_submission(submission, tmp_path)

    assert isinstance(result, SiteGenerationResult)
    assert result.tenant_id == "test_tenant"
    assert result.pages == ["about", "contact", "home", "services"]

    assert result.output_dir is not None
    web_dir = result.output_dir
    assert web_dir.exists()
    for page in result.pages:
        assert (web_dir / f"{page}.html").exists()
    assert (web_dir / "tokens.css").exists()


def test_generate_site_includes_reviews_when_present(tmp_path: Path):
    submission = _minimal_submission(tmp_path)
    submission.rating_value = 4.8
    submission.review_count = 120
    submission.testimonials = "Great work!"
    submission.emergency_service = "Yes"
    submission.pricing_shown = "Yes"
    submission.certifications = "Certified"

    result = generate_site_for_submission(submission, tmp_path)
    assert result.has_reviews is True
    assert "reviews" in result.pages
    assert result.trust_signal_count == 4
    reviews_html = (result.output_dir / "reviews.html").read_text(encoding="utf-8")
    assert "Great work!" in reviews_html
    assert "4.8" in reviews_html


def test_generate_site_omits_reviews_when_absent(tmp_path: Path):
    submission = _minimal_submission(tmp_path)
    result = generate_site_for_submission(submission, tmp_path)
    assert result.has_reviews is False
    assert "reviews" not in result.pages


def test_generated_home_contains_tenant_fields(tmp_path: Path):
    submission = _minimal_submission(tmp_path)
    result = generate_site_for_submission(submission, tmp_path)
    html = (result.output_dir / "home.html").read_text(encoding="utf-8")

    assert "Test Biz" in html
    assert "555-0000" in html
    assert "test@example.com" in html
    assert "Site by NetBuild.Pro" in html
    assert 'data-tenant-id="test_tenant"' in html
