"""Search criteria and legal routes never enter the access logger."""

import logging

import pytest

from abogalia_api.identity.logging import AuthAccessFilter


@pytest.mark.parametrize(
    "line",
    [
        "/api/public/professionals?name=PUBLIC_SYNTHETIC_SEARCH",
        "/api/public/professionals/00000000-0000-0000-0000-000000000001",
        "/api/legal-requests/PUBLIC_SYNTHETIC_ID",
        "/api/%70ublic/professionals?name=PUBLIC_SYNTHETIC_SEARCH",
        "/api/auth/session",
        "/api/professional/profile",
    ],
)
def test_sensitive_route_record_is_dropped_without_formatting(line):
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, __file__, 1, "%s %s %s", ("GET", "HTTP", line), None
    )
    assert not AuthAccessFilter().filter(record)


def test_public_health_record_is_still_allowed():
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        "%s %s %s",
        ("GET", "HTTP", "/api/health"),
        None,
    )
    assert AuthAccessFilter().filter(record)
