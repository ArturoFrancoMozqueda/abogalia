"""No network: verify fixed destinations, bounded health and sanitized failures."""

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "public_health", Path(__file__).parents[1] / "check_legalia_public.py"
)
health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(health)


class Response:
    status = 200

    def __init__(self, body=b'{"status":"ok","service":"abogalia-api"}'):
        self.body = body
        self.headers = {
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        }
        self.headers["Content-Type"] = (
            "application/json" if body.startswith(b"{") else "text/html"
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, bound):
        return self.body[:bound]


class PublicHealthTests(unittest.TestCase):
    def test_requests_are_fixed_and_never_forward_credentials(self):
        seen = []

        def opened(request, timeout):
            seen.append(request)
            self.assertEqual(timeout, 10)
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(set(request.headers), {"User-agent"})
            return Response(
                b"<html>synthetic</html>"
                if not request.full_url.endswith("health")
                else b'{"status":"ok","service":"abogalia-api"}'
            )

        with patch.object(
            health.urllib.request.OpenerDirector, "open", side_effect=opened
        ):
            self.assertEqual(health.check()["status"], "passed")
        self.assertEqual(
            [request.full_url for request in seen],
            [health.ORIGIN + path for path in ("/", "/registro", "/api/health")],
        )

    def test_provider_diagnostics_never_enter_output(self):
        with patch.object(
            health.urllib.request.OpenerDirector,
            "open",
            side_effect=RuntimeError("PUBLIC_SYNTHETIC_DIAGNOSTIC"),
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                result = health.check()
            self.assertEqual(output.getvalue(), "")
            self.assertNotIn("PUBLIC_SYNTHETIC_DIAGNOSTIC", json.dumps(result))
            self.assertEqual(result["status"], "failed")

    def test_oversize_health_cannot_pass(self):
        with patch.object(
            health.urllib.request.OpenerDirector,
            "open",
            return_value=Response(b" " * 4096),
        ):
            self.assertFalse(health.check()["components"]["api"])

    def test_redirect_never_produces_a_followup_request(self):
        self.assertIsNone(
            health.RejectRedirects().redirect_request(
                None, None, 302, "", {}, "https://untrusted.invalid"
            )
        )


if __name__ == "__main__":
    unittest.main()
