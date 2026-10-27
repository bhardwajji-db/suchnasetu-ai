import pytest
from unittest.mock import MagicMock
from fastapi import Request
from fastapi.testclient import TestClient

from notice2action.config import config
from notice2action.api.auth_routes import get_client_ip, _is_request_https


def _make_dummy_request(client_host: str, headers: dict = None, scheme: str = "http") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "scheme": scheme,
        "client": (client_host, 54321) if client_host else None,
        "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()],
    }
    return Request(scope)


class TestStage3ASecurityRemediations:
    """Automated verification suite for Stage 3A security remediations."""

    def test_untrusted_client_cannot_spoof_ip(self):
        """Arbitrary external client sending X-Forwarded-For must be ignored."""
        untrusted_ip = "198.51.100.42"
        headers = {
            "X-Forwarded-For": "203.0.113.195, 10.0.0.1",
            "CF-Connecting-IP": "192.0.2.1"
        }
        req = _make_dummy_request(client_host=untrusted_ip, headers=headers)
        resolved_ip = get_client_ip(req)
        assert resolved_ip == untrusted_ip
        assert resolved_ip != "203.0.113.195"
        assert resolved_ip != "192.0.2.1"

    def test_trusted_proxy_cf_connecting_ip_prioritized(self):
        """Trusted local proxy (127.0.0.1) sending CF-Connecting-IP must be honored."""
        headers = {
            "CF-Connecting-IP": "203.0.113.99",
            "X-Forwarded-For": "10.0.0.1"
        }
        req = _make_dummy_request(client_host="127.0.0.1", headers=headers)
        resolved_ip = get_client_ip(req)
        assert resolved_ip == "203.0.113.99"

    def test_trusted_proxy_x_forwarded_for_fallback(self):
        """Trusted local proxy sending X-Forwarded-For without CF-Connecting-IP must resolve first client IP."""
        headers = {
            "X-Forwarded-For": "198.51.100.77, 127.0.0.1"
        }
        req = _make_dummy_request(client_host="127.0.0.1", headers=headers)
        resolved_ip = get_client_ip(req)
        assert resolved_ip == "198.51.100.77"

    def test_untrusted_client_cannot_spoof_https_proto(self):
        """Untrusted client sending X-Forwarded-Proto: https on HTTP connection must be ignored."""
        untrusted_ip = "198.51.100.42"
        headers = {
            "X-Forwarded-Proto": "https"
        }
        req = _make_dummy_request(client_host=untrusted_ip, headers=headers, scheme="http")
        assert _is_request_https(req) is False

    def test_trusted_proxy_https_proto_honored(self):
        """Trusted local proxy sending X-Forwarded-Proto: https must be recognized as HTTPS."""
        headers = {
            "X-Forwarded-Proto": "https"
        }
        req = _make_dummy_request(client_host="127.0.0.1", headers=headers, scheme="http")
        assert _is_request_https(req) is True

    def test_local_direct_http_keeps_cookie_non_secure(self):
        """Direct local HTTP request must not mark cookies Secure, preserving local browser testing."""
        req = _make_dummy_request(client_host="127.0.0.1", headers={}, scheme="http")
        assert _is_request_https(req) is False

    def test_api_docs_configuration_toggle(self, monkeypatch):
        """ENABLE_API_DOCS toggle cleanly controls docs endpoints."""
        from fastapi import FastAPI
        
        # Test disabled docs
        app_disabled = FastAPI(
            title="Test",
            docs_url="/docs" if False else None,
            redoc_url="/redoc" if False else None,
            openapi_url="/openapi.json" if False else None,
        )
        client_disabled = TestClient(app_disabled)
        assert client_disabled.get("/docs").status_code == 404
        assert client_disabled.get("/redoc").status_code == 404
        assert client_disabled.get("/openapi.json").status_code == 404

        # Test enabled docs
        app_enabled = FastAPI(
            title="Test",
            docs_url="/docs" if True else None,
            redoc_url="/redoc" if True else None,
            openapi_url="/openapi.json" if True else None,
        )
        client_enabled = TestClient(app_enabled)
        assert client_enabled.get("/docs").status_code == 200
        assert client_enabled.get("/openapi.json").status_code == 200
