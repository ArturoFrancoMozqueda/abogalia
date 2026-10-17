"""Public directory with controlled synthetic guarded source; no database/network."""

import base64
import json
from contextlib import contextmanager
from copy import deepcopy
from threading import RLock
from urllib.parse import urlencode
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from abogalia_api.marketplace.directory import (
    MAX_SOURCE_ROWS,
    DirectoryError,
    DirectoryQuery,
    DirectoryService,
)
from abogalia_api.marketplace.router import router

PATH = "/api/public/professionals"


def publication(number, name="SYNTHETIC Ángela", area="SYNTHETIC Ámbito"):
    return {
        "public_id": str(UUID(int=number)),
        "display_name": name,
        "declared_area": area,
        "review": {"scope": "registry_record_checked", "checked_at": "2026-10-17T12:00:00Z"},
        "listing_version": 1,
        "public_context_label": "SYNTHETIC PRACTICE",
        "requestable": True,
    }


class SyntheticSource:
    def __init__(self, publications):
        self.publications = publications
        self.calls = 0
        self.lock = RLock()
        self.fail = False
        self.fail_exit = False

    @contextmanager
    def eligible_publications(self):
        with self.lock:
            self.calls += 1
            if self.fail:
                raise RuntimeError("SYNTHETIC_PRIVATE_SOURCE_DIAGNOSTIC")
            yield deepcopy(self.publications)
            if self.fail_exit:
                raise RuntimeError("SYNTHETIC_PRIVATE_SOURCE_DIAGNOSTIC")


def client_for(source=None):
    app = FastAPI()
    app.state.directory = DirectoryService(source)
    app.include_router(router)
    return TestClient(app)


def assert_safe(response, status, code=None):
    assert response.status_code == status
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "set-cookie" not in response.headers
    assert "authorization" not in response.headers
    assert "SYNTHETIC_PRIVATE_SOURCE_DIAGNOSTIC" not in response.text
    if code:
        assert response.json()["error"]["code"] == code
        assert set(response.json()) == {"error"}
        assert set(response.json()["error"]) == {"code", "message"}


def test_unconfigured_source_is_unavailable_not_empty_fixture():
    client = client_for()
    assert_safe(client.get(PATH), 503, "OPERATION_UNAVAILABLE")
    assert_safe(client.get(f"{PATH}/{UUID(int=1)}"), 503, "OPERATION_UNAVAILABLE")
    app = FastAPI()
    app.include_router(router)
    assert_safe(TestClient(app).get(PATH), 503, "OPERATION_UNAVAILABLE")


def test_guarded_empty_source_is_real_empty_and_rechecked_for_each_request():
    source = SyntheticSource([])
    client = client_for(source)
    assert client.get(PATH).json() == {"items": [], "next_cursor": None, "order": "display_name"}
    source.publications.append(publication(1))
    response = client.get(PATH)
    assert_safe(response, 200)
    assert response.json()["items"] == source.publications
    assert source.calls == 2


def test_public_projection_exactly_allowlisted_no_identity_cookies_or_actors():
    source = SyntheticSource([publication(1)])
    client = client_for(source)
    response = client.get(PATH, headers={"Cookie": "synthetic=PUBLIC_TEST_MARKER"})
    assert_safe(response, 200)
    assert response.json()["items"] == source.publications
    assert "PUBLIC_TEST_MARKER" not in response.text
    assert set(response.json()["items"][0]) == {
        "public_id",
        "display_name",
        "declared_area",
        "review",
        "listing_version",
        "public_context_label",
        "requestable",
    }


@pytest.mark.parametrize("name,area", [("a\u0301NGELA", None), (None, "a\u0301MBITO")])
def test_nfc_casefold_matching_public_fields(name, area):
    client = client_for(SyntheticSource([publication(1), publication(2, "SYNTHETIC Other", None)]))
    query = {key: value for key, value in {"name": name, "declared_area": area}.items() if value}
    result = client.get(PATH, params=query).json()
    assert [item["public_id"] for item in result["items"]] == [str(UUID(int=1))]


def test_casefold_expansion_and_field_intersection_are_literal():
    source = SyntheticSource(
        [
            publication(1, "SYNTHETIC Straße", "SYNTHETIC A%_.*"),
            publication(2, "SYNTHETIC Street", "SYNTHETIC Different"),
        ]
    )
    client = client_for(source)
    response = client.get(PATH, params={"name": "STRASSE", "declared_area": "%_.*"})
    assert [p["public_id"] for p in response.json()["items"]] == [str(UUID(int=1))]
    assert client.get(PATH, params={"name": "Street", "declared_area": "%"}).json()["items"] == []
    assert client.get(PATH, params={"name": "[a-z]+"}).json()["items"] == []


def test_default_page_twenty_stable_order_and_maximum_fifty():
    entries = [publication(i, "SYNTHETIC Same") for i in range(60, 0, -1)]
    client = client_for(SyntheticSource(entries))
    first = client.get(PATH).json()
    assert len(first["items"]) == 20
    assert [p["public_id"] for p in first["items"]] == [str(UUID(int=i)) for i in range(1, 21)]
    assert first["next_cursor"] is not None
    assert len(client.get(PATH, params={"limit": "50"}).json()["items"]) == 50


@pytest.mark.parametrize(
    "query",
    [
        "name=",
        "name=%20%20",
        "declared_area=",
        "name=a&name=b",
        "limit=1&limit=2",
        "q=anything",
        "email=anything",
        "context_id=anything",
        "unknown=x",
        "cursor=",
        "limit=0",
        "limit=-1",
        "limit=51",
        "limit=01",
        "limit=1.0",
        "limit=true",
        "limit=%2B1",
        "limit=500",
        "limit=%D9%A1",
        "name=%00",
        "name=%0A",
        "name=%E2%80%8B",
        "name=%FF",
        "name=%ZZ",
        "name=%",
        "name",
        "name=a&&limit=1",
        "cursor=%25",
        "cursor=" + "a" * 513,
        "name=" + "a" * 81,
        "name=" + "a" * 41 + "&declared_area=" + "b" * 40,
        "cursor=" + "a" * 2050,
    ],
)
def test_invalid_query_uniform_sanitized_without_touching_source(query):
    source = SyntheticSource([publication(1)])
    response = client_for(source).get(PATH + "?" + query)
    assert_safe(response, 422, "INVALID_REQUEST")
    assert source.calls == 0


def test_filter_length_is_after_nfc_and_total_eighty_not_casefold():
    text = "a\u0301" * 80
    client = client_for(SyntheticSource([]))
    assert_safe(client.get(PATH, params={"name": text}), 200)
    assert_safe(client.get(PATH, params={"name": "a" * 40, "declared_area": "b" * 40}), 200)
    assert_safe(client.get(PATH, params={"name": "a" * 40, "declared_area": "b" * 41}), 422)


def test_query_byte_cap_is_not_character_cap():
    # Each percent-encoded Unicode codepoint consumes multiple raw query bytes.
    query = urlencode({"name": "á" * 80, "cursor": "a" * 512})
    assert len(query.encode()) < 2048
    assert DirectoryQuery.parse(query.encode()).name == "á" * 80
    with pytest.raises(DirectoryError) as caught:
        DirectoryQuery.parse(b"name=" + b"a" * 2048)
    assert caught.value.code == "INVALID_REQUEST"


@pytest.mark.parametrize("authorization", ["", "PUBLIC_SYNTHETIC_HEADER"])
def test_authorization_presence_rejected_without_identity_or_source(authorization):
    source = SyntheticSource([])
    response = client_for(source).get(PATH, headers={"Authorization": authorization})
    assert_safe(response, 403, "REQUEST_FORBIDDEN")
    assert source.calls == 0


def test_get_body_rejected_and_not_reflected():
    source = SyntheticSource([])
    response = client_for(source).request("GET", PATH, content="PUBLIC_SYNTHETIC_BODY")
    assert_safe(response, 422, "INVALID_REQUEST")
    assert "PUBLIC_SYNTHETIC_BODY" not in response.text
    assert source.calls == 0


def test_detail_no_queries_uniform_unknown_and_invalid_public_ids():
    source = SyntheticSource([publication(1)])
    client = client_for(source)
    response = client.get(f"{PATH}/{UUID(int=1)}")
    assert_safe(response, 200)
    assert response.json() == {"professional": publication(1)}
    assert_safe(client.get(f"{PATH}/{UUID(int=1)}?limit=1"), 422, "INVALID_REQUEST")
    missing = client.get(f"{PATH}/{UUID(int=2)}")
    malformed = client.get(f"{PATH}/not-a-public-id")
    zero = client.get(f"{PATH}/{UUID(int=0)}")
    for response in (missing, malformed, zero):
        assert_safe(response, 404, "RESOURCE_UNAVAILABLE")
    assert missing.content == malformed.content == zero.content


def test_cursor_paginates_and_binds_filters_page_size_and_service_lifetime():
    entries = [publication(i, f"SYNTHETIC {i:02}") for i in range(1, 6)]
    source = SyntheticSource(entries)
    client = client_for(source)
    query = {"name": "SYNTHETIC", "limit": "2"}
    first = client.get(PATH, params=query).json()
    token = first["next_cursor"]
    assert len(token) <= 512
    assert b"SYNTHETIC" not in base64.urlsafe_b64decode(token)
    second = client.get(PATH, params={**query, "cursor": token}).json()
    assert [p["public_id"] for p in second["items"]] == [str(UUID(int=3)), str(UUID(int=4))]
    last = client.get(PATH, params={**query, "cursor": second["next_cursor"]}).json()
    assert [p["public_id"] for p in last["items"]] == [str(UUID(int=5))]
    assert last["next_cursor"] is None
    for wrong_query in ({"limit": "2"}, {"name": "OTHER", "limit": "2"}, {"name": "SYNTHETIC"}):
        assert_safe(
            client.get(PATH, params={**wrong_query, "cursor": token}), 422, "INVALID_REQUEST"
        )
    assert_safe(client_for(source).get(PATH, params={**query, "cursor": token}), 422)
    mutated = token[:-8] + ("A" if token[-8] != "A" else "B") + token[-7:]
    assert_safe(client.get(PATH, params={**query, "cursor": mutated}), 422)


def test_retired_projection_between_pages_is_not_resurrected_by_cursor():
    entries = [publication(i, f"SYNTHETIC {i:02}") for i in range(1, 5)]
    source = SyntheticSource(entries)
    client = client_for(source)
    token = client.get(PATH, params={"limit": "1"}).json()["next_cursor"]
    source.publications = [entries[0], entries[2], entries[3]]
    response = client.get(PATH, params={"limit": "1", "cursor": token})
    assert_safe(response, 200)
    assert response.json()["items"][0]["public_id"] == str(UUID(int=3))
    assert_safe(client.get(f"{PATH}/{UUID(int=2)}"), 404)
    assert source.calls == 3


@pytest.mark.parametrize("change", ["retire", "rename"])
def test_missing_or_changed_anchor_requires_restart_instead_of_position_fallback(change):
    source = SyntheticSource([publication(1, "SYNTHETIC A"), publication(2, "SYNTHETIC B")])
    client = client_for(source)
    token = client.get(PATH, params={"limit": "1"}).json()["next_cursor"]
    if change == "retire":
        source.publications.pop(0)
    else:
        source.publications[0]["display_name"] = "SYNTHETIC Z"
    assert_safe(client.get(PATH, params={"limit": "1", "cursor": token}), 409, "VERSION_CONFLICT")


@pytest.mark.parametrize(
    "field,value",
    [
        ("legal_name", "SYNTHETIC_PRIVATE_FIELD"),
        ("context_id", "SYNTHETIC_PRIVATE_FIELD"),
        ("requestable", False),
        ("requestable", 1),
        ("listing_version", True),
        ("review", {"scope": "identity_verified", "checked_at": "2026-10-17T00:00:00Z"}),
        ("review", {"scope": "registry_record_checked", "checked_at": "2026-10-17"}),
        ("public_context_label", ""),
        ("display_name", "SYNTHETIC\nPRIVATE"),
    ],
)
def test_source_cannot_leak_private_aggregates_or_invalid_public_projections(field, value):
    entry = publication(1)
    entry[field] = value
    client = client_for(SyntheticSource([entry]))
    for url in (PATH, f"{PATH}/{UUID(int=1)}"):
        response = client.get(url)
        assert_safe(response, 503, "OPERATION_UNAVAILABLE")
        assert "SYNTHETIC_PRIVATE_FIELD" not in response.text


def test_source_failures_and_guard_revalidation_failure_are_sanitized():
    source = SyntheticSource([publication(1)])
    client = client_for(source)
    for flag in ("fail", "fail_exit"):
        setattr(source, flag, True)
        for path in (PATH, f"{PATH}/{UUID(int=1)}"):
            response = client.get(path)
            assert_safe(response, 503, "OPERATION_UNAVAILABLE")
            assert "SYNTHETIC Ángela" not in response.text
        setattr(source, flag, False)


def test_duplicate_public_id_fails_closed_instead_of_ambiguous_recipient():
    first = publication(1)
    second = publication(1, "SYNTHETIC Other Context")
    response = client_for(SyntheticSource([first, second])).get(PATH)
    assert_safe(response, 503, "OPERATION_UNAVAILABLE")


def test_encoded_output_is_detached_from_mutable_source():
    source = SyntheticSource([publication(1)])
    service = DirectoryService(source)
    encoded = service.list(DirectoryQuery.parse(b""))
    source.publications[0]["display_name"] = "SYNTHETIC CHANGED"
    assert json.loads(encoded)["items"][0]["display_name"] == "SYNTHETIC Ángela"


def test_adapter_rows_are_bounded_without_silent_truncation_or_infinite_iteration():
    class OversizedSource:
        yielded = 0

        @contextmanager
        def eligible_publications(self):
            def rows():
                for number in range(1, MAX_SOURCE_ROWS + 100):
                    self.yielded += 1
                    yield publication(number)

            yield rows()

    source = OversizedSource()
    response = client_for(source).get(PATH)
    assert_safe(response, 503, "OPERATION_UNAVAILABLE")
    assert source.yielded == MAX_SOURCE_ROWS + 1


def test_detail_withdrawal_revalidates_instead_of_reusing_old_public_projection():
    source = SyntheticSource([publication(1)])
    client = client_for(source)
    assert_safe(client.get(f"{PATH}/{UUID(int=1)}"), 200)
    source.publications = []
    response = client.get(f"{PATH}/{UUID(int=1)}")
    assert_safe(response, 404, "RESOURCE_UNAVAILABLE")
    assert "SYNTHETIC Ángela" not in response.text
