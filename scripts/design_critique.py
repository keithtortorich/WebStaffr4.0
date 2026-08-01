#!/usr/bin/env python3
"""On-demand design critique for one rendered tenant site page.

This is a founder/session tool, not a route -- deliberately not mounted
into webstaffr/app.py's composition root, because it isn't meant to be
callable by an arbitrary HTTP request. It's invoked by hand (or by a
future Cowork skill loop) when someone actually wants a design opinion,
which is what keeps the OpenRouter cost to exactly the calls someone
asked for. See webstaffr/integrations/design_critique/client.py's module
docstring for why this stays out of the automatic render path entirely.

Usage:
    python scripts/design_critique.py <tenant_id> [--page home|about|contact|service:<slug>] [--base-url http://localhost:8000]

Requires the target app to already be running and reachable at --base-url
(defaults to http://localhost:8000), and OPENROUTER_API_KEY set in the
environment -- this script fetches real rendered HTML over HTTP rather
than re-implementing rendering, so it reviews exactly what a visitor
would actually see.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _page_path(tenant_id: str, page: str) -> str:
    base = f"/sites/{tenant_id}/web"
    if page == "home":
        return base
    if page in ("about", "contact"):
        return f"{base}/{page}"
    if page.startswith("service:"):
        slug = page.split(":", 1)[1]
        return f"{base}/services/{slug}"
    raise ValueError(f"unrecognized --page value: {page!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tenant_id")
    parser.add_argument("--page", default="home", help="home | about | contact | service:<slug>")
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    import httpx

    from webstaffr.integrations.design_critique.client import (
        DesignCritiqueError,
        DesignCritiqueNotConfiguredError,
        NullDesignCritiqueClient,
        OpenRouterDesignCritiqueClient,
    )

    try:
        critique_client = OpenRouterDesignCritiqueClient()
    except DesignCritiqueNotConfiguredError as exc:
        print(f"[not configured] {exc}", file=sys.stderr)
        print(NullDesignCritiqueClient().critique("", page_label=args.page))
        return 1

    path = _page_path(args.tenant_id, args.page)
    url = f"{args.base_url.rstrip('/')}{path}"

    try:
        resp = httpx.get(url, timeout=15.0)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"[fetch failed] could not fetch {url}: {exc}", file=sys.stderr)
        return 1

    print(f"Reviewing {url} ...", file=sys.stderr)
    try:
        feedback = critique_client.critique(resp.text, page_label=args.page)
    except DesignCritiqueError as exc:
        print(f"[critique failed] {exc}", file=sys.stderr)
        return 1

    print(feedback)
    return 0


if __name__ == "__main__":
    sys.exit(main())
