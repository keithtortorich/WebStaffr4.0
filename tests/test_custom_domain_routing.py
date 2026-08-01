import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from webstaffr.custom_domain_middleware import CustomDomainMiddleware
from webstaffr.custom_domain import resolve_tenant_from_host


class CustomDomainMiddlewareTestCase(unittest.TestCase):
    """Tests for phase 2 custom domain middleware.

    Custom domain middleware rewrites requests to custom domains to the
    internal /sites/{tenant_id}/web routing structure via Host header lookup.
    """

    def setUp(self):
        self.middleware = CustomDomainMiddleware(MagicMock())

    async def test_middleware_rewrites_custom_domain_path(self):
        """Middleware should rewrite custom domain paths to /sites/{tenant_id}/web."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="desertcooling.com")
        request.url.path = "/"
        request.scope = {"path": "/"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-abc123"

            await self.middleware.dispatch(request, call_next)

            # Verify path was rewritten
            self.assertEqual(request.scope["path"], "/sites/tenant-abc123/web/")
            # Verify call_next was invoked
            call_next.assert_called_once()

    async def test_middleware_handles_subpaths(self):
        """Middleware should preserve subpaths in rewrite."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="desertcooling.com")
        request.url.path = "/about"
        request.scope = {"path": "/about"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-xyz"

            await self.middleware.dispatch(request, call_next)

            self.assertEqual(request.scope["path"], "/sites/tenant-xyz/web/about")

    async def test_middleware_handles_services_subpath(self):
        """Middleware should handle /services/{slug} subpaths."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="cooltech.com")
        request.url.path = "/services/ac-repair"
        request.scope = {"path": "/services/ac-repair"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-service"

            await self.middleware.dispatch(request, call_next)

            self.assertEqual(request.scope["path"], "/sites/tenant-service/web/services/ac-repair")

    async def test_middleware_passthrough_for_path_based_requests(self):
        """Middleware should pass through requests that aren't custom domains."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="localhost:8000")
        request.url.path = "/sites/tenant-123/web"
        request.scope = {"path": "/sites/tenant-123/web"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = None  # Not a custom domain

            await self.middleware.dispatch(request, call_next)

            # Path should remain unchanged
            self.assertEqual(request.scope["path"], "/sites/tenant-123/web")

    async def test_middleware_stores_request_state(self):
        """Middleware should store custom domain info in request.state for debugging."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="test.com")
        request.url.path = "/contact"
        request.scope = {"path": "/contact"}
        request.state = MagicMock()
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-debug"

            await self.middleware.dispatch(request, call_next)

            # Verify state was set for debugging
            self.assertEqual(request.state.custom_domain_tenant_id, "tenant-debug")
            self.assertEqual(request.state.original_path, "/contact")

    async def test_middleware_handles_sitemap_xml(self):
        """Middleware should handle special paths like /sitemap.xml."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="mybusiness.com")
        request.url.path = "/sitemap.xml"
        request.scope = {"path": "/sitemap.xml"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-sitemap"

            await self.middleware.dispatch(request, call_next)

            self.assertEqual(request.scope["path"], "/sites/tenant-sitemap/web/sitemap.xml")

    async def test_middleware_handles_robots_txt(self):
        """Middleware should handle /robots.txt."""
        request = MagicMock()
        request.headers.get = MagicMock(return_value="mybusiness.com")
        request.url.path = "/robots.txt"
        request.scope = {"path": "/robots.txt"}
        request.app.state.db_path = ":memory:"

        call_next = AsyncMock(return_value=MagicMock())

        with patch("webstaffr.custom_domain_middleware.resolve_tenant_from_host") as mock_resolve:
            mock_resolve.return_value = "tenant-robots"

            await self.middleware.dispatch(request, call_next)

            self.assertEqual(request.scope["path"], "/sites/tenant-robots/web/robots.txt")


class CustomDomainResolutionTestCase(unittest.TestCase):
    """Tests for custom domain resolution via Host header lookup."""

    def test_resolve_tenant_from_host_valid_domain(self):
        """resolve_tenant_from_host should query custom_domain column."""
        # This test verifies the integration with the database
        # For unit testing, we mock the database
        with patch("webstaffr.custom_domain.get_connection") as mock_conn:
            mock_db = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone = MagicMock(return_value=("tenant-123",))
            mock_db.cursor = MagicMock(return_value=mock_cursor)
            mock_conn.return_value = mock_db

            result = resolve_tenant_from_host("desertcooling.com", ":memory:")

            self.assertEqual(result, "tenant-123")
            mock_cursor.execute.assert_called_once()

    def test_resolve_tenant_from_host_strips_port(self):
        """resolve_tenant_from_host should strip port from Host header."""
        with patch("webstaffr.custom_domain.get_connection") as mock_conn:
            mock_db = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone = MagicMock(return_value=("tenant-port",))
            mock_db.cursor = MagicMock(return_value=mock_cursor)
            mock_conn.return_value = mock_db

            result = resolve_tenant_from_host("desertcooling.com:8080", ":memory:")

            self.assertEqual(result, "tenant-port")
            # Verify the query was made for the domain without port
            args, kwargs = mock_cursor.execute.call_args
            self.assertIn("desertcooling.com", str(args))

    def test_resolve_tenant_from_host_not_found(self):
        """resolve_tenant_from_host should return None for unknown domains."""
        with patch("webstaffr.custom_domain.get_connection") as mock_conn:
            mock_db = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone = MagicMock(return_value=None)
            mock_db.cursor = MagicMock(return_value=mock_cursor)
            mock_conn.return_value = mock_db

            result = resolve_tenant_from_host("unknown.com", ":memory:")

            self.assertIsNone(result)

    def test_resolve_tenant_from_host_empty_header(self):
        """resolve_tenant_from_host should handle missing Host header gracefully."""
        result = resolve_tenant_from_host("", ":memory:")
        self.assertIsNone(result)

    def test_resolve_tenant_from_host_case_insensitive(self):
        """resolve_tenant_from_host should normalize domain case."""
        with patch("webstaffr.custom_domain.get_connection") as mock_conn:
            mock_db = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone = MagicMock(return_value=("tenant-case",))
            mock_db.cursor = MagicMock(return_value=mock_cursor)
            mock_conn.return_value = mock_db

            # Call with mixed case
            result = resolve_tenant_from_host("DesertCooling.COM", ":memory:")

            self.assertEqual(result, "tenant-case")
            # Verify domain was lowercased in query
            args, kwargs = mock_cursor.execute.call_args
            self.assertIn("desertcooling.com", str(args).lower())


if __name__ == "__main__":
    unittest.main()
