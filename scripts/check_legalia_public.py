"""Explicit read-only public health check; fixed destinations and aggregate output only."""

import argparse
import json
import urllib.error
import urllib.request

ORIGIN = "https://legalia-web.legaliasupport.workers.dev"


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not follow even a same-host redirect: the expected routes return200.
        return None


def check():
    client = urllib.request.build_opener(RejectRedirects())
    results = {}
    for component, path, private in (
        ("web", "/", False),
        ("access", "/registro", True),
        ("api", "/api/health", True),
    ):
        passed = False
        try:
            request = urllib.request.Request(
                ORIGIN + path,
                headers={"User-Agent": "Legalia-Deployment-Verification/1.0"},
            )
            # No cookie jar, Authorization, email, query, client input or provider key.
            with client.open(request, timeout=10) as response:
                passed = (
                    response.status == 200
                    and response.headers.get("X-Content-Type-Options") == "nosniff"
                )
                if private:
                    passed = passed and "no-store" in response.headers.get(
                        "Cache-Control", ""
                    )
                if component == "api":
                    body = response.read(2049)
                    passed = (
                        passed
                        and len(body) <= 2048
                        and json.loads(body)
                        == {"status": "ok", "service": "abogalia-api"}
                    )
                else:
                    passed = passed and response.headers.get(
                        "Content-Type", ""
                    ).startswith("text/html")
        except Exception:  # noqa: BLE001 - Never forward transport or response diagnostics.
            # Never expose exceptions, response bodies, headers or transport diagnostics.
            passed = False
        results[component] = bool(passed)
    return {
        "status": "passed" if all(results.values()) else "failed",
        "components": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="store_true", help="Make three public GET requests now"
    )
    if not parser.parse_args().run:
        parser.print_help()
        return 0
    result = check()
    print(json.dumps(result))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
