"""Middleware to handle custom domain routing for phase 2 feature.

Custom domains allow tenants to serve sites at custom domains (e.g., desertcooling.com)
instead of path-based /sites/{tenant_id}/web routes. This middleware intercepts requests
to custom domains, resolves the tenant_id via Host header lookup, and rewrites the request
path to the internal path-based routing mechanism.

This approach:
- Avoids duplicate route handlers
- Keeps custom domain logic localized
- Reuses existing path-based rendering pipeline
- Maintains clean separation of concerns
"""

from __future__ import annotations

import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .custom_domain import resolve_tenant_from_host

logger = logging.getLogger("webstaffr.custom_domain_middleware")


class CustomDomainMiddleware(BaseHTTPMiddleware):
    """Middleware to handle custom domain routing via Host header lookup.

    When a request arrives with a Host header matching a registered custom_domain:
    1. Resolve the tenant_id from the custom_domain column
    2. Rewrite the request path to /sites/{tenant_id}/web{original_path}
    3. Continue normal routing (path-based handlers take over)

    If Host header doesn't match a custom domain, request passes through unchanged
    (path-based routing continues as normal).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercept request and rewrite path if it's a custom domain request."""
        host = request.headers.get("Host", "")
        tenant_id = resolve_tenant_from_host(host, request.app.state.db_path)

        if tenant_id:
            # This is a custom domain request; rewrite path for internal routing
            original_path = request.url.path
            rewritten_path = f"/sites/{tenant_id}/web{original_path}"

            # Store original path in request state for debugging/logging if needed
            request.state.custom_domain_tenant_id = tenant_id
            request.state.original_path = original_path

            # Rewrite scope for FastAPI routing
            # This causes FastAPI to route as if the request came to /sites/{tenant_id}/web{path}
            request.scope["path"] = rewritten_path

            logger.debug(
                "custom_domain_rewrite host=%s tenant_id=%s original_path=%s rewritten_path=%s",
                host,
                tenant_id,
                original_path,
                rewritten_path,
            )

        return await call_next(request)
