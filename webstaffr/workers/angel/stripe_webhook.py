"""Stripe webhook signature verification.

Stripe signs outgoing webhooks with HMAC-SHA256 over the raw request body.
The signature is sent in the X-Stripe-Signature header as:
  t=<timestamp>,v1=<signature>

This module provides signature verification matching Stripe's documented
webhook security: https://stripe.com/docs/webhooks/signatures
"""

from __future__ import annotations

import hmac
import hashlib
import os
import time
from typing import Optional, Protocol


class SharedSecretVerifier(Protocol):
    def verify(self, provided: Optional[str], raw_body: Optional[bytes] = None) -> bool: ...


class NullStripeWebhookVerifier:
    """Accepts everything -- safe default for tests and before
    STRIPE_WEBHOOK_SECRET is set. Matches the Null-verifier pattern
    used by GHL and book API verifiers."""

    def verify(self, provided: Optional[str], raw_body: Optional[bytes] = None) -> bool:
        return True


class StripeSignatureVerifier:
    """Verifies Stripe's HMAC-SHA256 signature on webhook payloads.

    Stripe sends X-Stripe-Signature as: t=<timestamp>,v1=<sig>
    We verify:
    1. Signature was generated within the last 5 minutes (prevents replay)
    2. HMAC-SHA256(<secret>, <timestamp>.<raw_body>) matches the provided sig
    """

    # Stripe recommends checking signature is within 5 minutes (300s)
    MAX_SIGNATURE_AGE_SECONDS = 300

    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("StripeSignatureVerifier requires a non-empty secret.")
        self._secret = secret

    def verify(self, provided: Optional[str], raw_body: Optional[bytes] = None) -> bool:
        """Verify Stripe signature. Returns False on any failure rather than
        raising, so callers always treat False as 'reject' without special
        exception handling.

        raw_body is required for a real check: HMAC-SHA256 is computed over
        <timestamp>.<raw_body>, so without the exact bytes Stripe signed,
        no comparison can be trusted. Missing raw_body fails closed rather
        than falling back to a no-op check."""
        if not provided or raw_body is None:
            return False

        try:
            parts = {}
            for part in provided.split(","):
                key, value = part.split("=", 1)
                parts[key] = value

            timestamp_str = parts.get("t")
            provided_sig = parts.get("v1")

            if not timestamp_str or not provided_sig:
                return False

            timestamp = int(timestamp_str)
            now = int(time.time())

            # Check signature is within 5 minutes (replay protection)
            if abs(now - timestamp) > self.MAX_SIGNATURE_AGE_SECONDS:
                return False

            signed_payload = f"{timestamp_str}.".encode("utf-8") + raw_body
            expected_sig = hmac.new(
                self._secret.encode("utf-8"), signed_payload, hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, provided_sig)
        except (ValueError, KeyError):
            return False


def stripe_webhook_verifier_from_env() -> SharedSecretVerifier:
    """STRIPE_WEBHOOK_SECRET set -> real verification of Stripe signatures.
    Unset -> Null verifier. Follows the same pattern as ghl_webhook_verifier_from_env
    and book_api_verifier_from_env: never silently construct something that will
    fail on first use, and never require credentials to run tests."""
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if secret:
        return StripeSignatureVerifier(secret)
    return NullStripeWebhookVerifier()
