"""Bounded public directory with fresh trusted projections and opaque continuation.

The source adapter, not a cursor or a snapshot fixture, is responsible for holding
and revalidating publication eligibility through the guarded serialization boundary.
No search history, public projection cache, or fixture fallback is stored here.
"""

import hashlib
import hmac
import json
import re
import secrets
import unicodedata
from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from urllib.parse import parse_qsl
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

# Adapter fault guard, not a maximum number of professionals in the product.
# A larger directory needs a guarded, paged production adapter; never truncate it.
MAX_SOURCE_ROWS = 1000

_MESSAGES = {
    "INVALID_REQUEST": "Revisa los datos de la solicitud.",
    "RESOURCE_UNAVAILABLE": "El recurso no está disponible.",
    "OPERATION_UNAVAILABLE": "La operación no está disponible temporalmente.",
    "VERSION_CONFLICT": "La información cambió. Actualiza antes de continuar.",
    "REQUEST_FORBIDDEN": "La operación no está permitida.",
}
_STATUSES = {
    "INVALID_REQUEST": 422,
    "RESOURCE_UNAVAILABLE": 404,
    "OPERATION_UNAVAILABLE": 503,
    "VERSION_CONFLICT": 409,
    "REQUEST_FORBIDDEN": 403,
}


class DirectoryError(Exception):
    """Fixed public diagnostics without input, source details, or credentials."""

    def __init__(self, code: str):
        self.code = code
        self.status = _STATUSES[code]
        super().__init__(code)

    def body(self):
        return {"error": {"code": self.code, "message": _MESSAGES[self.code]}}


def normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def has_controls(value: str) -> bool:
    return any(unicodedata.category(character).startswith("C") for character in value)


def public_uuid(value: str) -> str:
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError, TypeError):
        raise DirectoryError("RESOURCE_UNAVAILABLE") from None
    if parsed.int == 0 or str(parsed) != value:
        raise DirectoryError("RESOURCE_UNAVAILABLE")
    return value


@dataclass(frozen=True, repr=False)
class DirectoryQuery:
    name: str | None = None
    declared_area: str | None = None
    limit: int = 20
    cursor: str | None = None

    @classmethod
    def parse(cls, raw: bytes, *, detail: bool = False):
        if len(raw) > 2048:
            raise DirectoryError("INVALID_REQUEST")
        try:
            decoded = raw.decode("utf-8", errors="strict")
            if re.search(r"%(?![0-9a-fA-F]{2})", decoded):
                raise ValueError
            pairs = parse_qsl(decoded, keep_blank_values=True, strict_parsing=True, errors="strict")
        except (UnicodeError, ValueError):
            raise DirectoryError("INVALID_REQUEST") from None
        if detail and pairs:
            raise DirectoryError("INVALID_REQUEST")
        values = {}
        for name, value in pairs:
            if (
                name not in {"name", "declared_area", "limit", "cursor"}
                or name in values
                or not value
                or has_controls(name)
                or has_controls(value)
            ):
                raise DirectoryError("INVALID_REQUEST")
            values[name] = value
        for key in ("name", "declared_area"):
            if key in values:
                values[key] = unicodedata.normalize("NFC", values[key]).strip()
                if not 1 <= len(values[key]) <= 80:
                    raise DirectoryError("INVALID_REQUEST")
        if sum(len(values.get(key, "")) for key in ("name", "declared_area")) > 80:
            raise DirectoryError("INVALID_REQUEST")
        limit = values.get("limit", "20")
        if not re.fullmatch(r"[1-9][0-9]?", limit) or int(limit) > 50:
            raise DirectoryError("INVALID_REQUEST")
        cursor = values.get("cursor")
        if cursor is not None and (
            len(cursor) > 512 or not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", cursor)
        ):
            raise DirectoryError("INVALID_REQUEST")
        return cls(values.get("name"), values.get("declared_area"), int(limit), cursor)


class _PublicModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)

    def __repr_args__(self):
        return []


class _Review(_PublicModel):
    scope: Literal["registry_record_checked"]
    checked_at: str = Field(min_length=1, max_length=40)

    @field_validator("checked_at")
    @classmethod
    def valid_time(cls, value):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid public projection") from None
        if parsed.utcoffset() is None or has_controls(value):
            raise ValueError("Invalid public projection")
        return value


class _Publication(_PublicModel):
    public_id: str
    display_name: str = Field(min_length=1, max_length=120)
    declared_area: str | None = Field(default=None, max_length=240)
    review: _Review
    listing_version: int = Field(gt=0, le=2**31 - 1)
    public_context_label: str = Field(min_length=1, max_length=120)
    requestable: Literal[True]

    @field_validator("requestable", mode="before")
    @classmethod
    def receiving_only(cls, value):
        if value is not True:
            raise ValueError("Invalid public projection")
        return value

    @field_validator("public_id")
    @classmethod
    def valid_id(cls, value):
        return public_uuid(value)

    @field_validator("display_name", "declared_area", "public_context_label")
    @classmethod
    def safe_text(cls, value):
        if value is not None and (not value.strip() or has_controls(value)):
            raise ValueError("Invalid public projection")
        return value


class DirectorySource(Protocol):
    """Only eligible allowlisted C03 projections, guarded through serialization.

    A production adapter must lock/revalidate publication, account, context and
    recipient eligibility until this context exits. It must not return private
    profile aggregates or an unguarded stale cache. No adapter is enabled by default.
    """

    def eligible_publications(self) -> AbstractContextManager[Iterable[Mapping[str, object]]]: ...


def _encoded(body) -> bytes:
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


class DirectoryService:
    """Dependency injected directory. Restart invalidates continuation safely."""

    def __init__(self, source: DirectorySource | None = None):
        self.source = source
        self._cipher = Fernet(Fernet.generate_key())
        self._binding_key = secrets.token_bytes(32)

    def _fingerprint(self, value) -> str:
        return hmac.new(self._binding_key, _encoded(value), hashlib.sha256).hexdigest()

    def _binding(self, query: DirectoryQuery) -> str:
        return self._fingerprint(
            [
                "directory-v1",
                normalized(query.name) if query.name else None,
                normalized(query.declared_area) if query.declared_area else None,
                query.limit,
                "display_name",
            ]
        )

    def _read_cursor(self, query):
        if query.cursor is None:
            return None
        try:
            payload = json.loads(self._cipher.decrypt(query.cursor.encode("ascii")))
            if (
                not isinstance(payload, list)
                or len(payload) != 4
                or payload[0] != 1
                or not all(isinstance(item, str) for item in payload[1:])
                or not hmac.compare_digest(payload[1], self._binding(query))
            ):
                raise ValueError
            public_uuid(payload[2])
            return payload[2], payload[3]
        except (InvalidToken, UnicodeError, ValueError, TypeError, DirectoryError):
            raise DirectoryError("INVALID_REQUEST") from None

    def _publications(self, entries):
        try:
            publications = []
            for index, entry in enumerate(entries):
                if index >= MAX_SOURCE_ROWS:
                    raise DirectoryError("OPERATION_UNAVAILABLE")
                publications.append(_Publication.model_validate(entry).model_dump())
        except (ValidationError, DirectoryError):
            raise DirectoryError("OPERATION_UNAVAILABLE") from None
        if len({item["public_id"] for item in publications}) != len(publications):
            raise DirectoryError("OPERATION_UNAVAILABLE")
        return publications

    def list(self, query: DirectoryQuery) -> bytes:
        anchor = self._read_cursor(query)
        if self.source is None:
            raise DirectoryError("OPERATION_UNAVAILABLE")
        # The source boundary covers fresh projection checks and JSON encoding.
        with self.source.eligible_publications() as entries:
            publications = self._publications(entries)
            matches = [
                item
                for item in publications
                if (
                    query.name is None or normalized(query.name) in normalized(item["display_name"])
                )
                and (
                    query.declared_area is None
                    or (
                        item["declared_area"] is not None
                        and normalized(query.declared_area) in normalized(item["declared_area"])
                    )
                )
            ]
            matches.sort(key=lambda item: (normalized(item["display_name"]), item["public_id"]))
            start = 0
            if anchor is not None:
                for position, item in enumerate(matches):
                    if item["public_id"] == anchor[0]:
                        if not hmac.compare_digest(
                            anchor[1], self._fingerprint(normalized(item["display_name"]))
                        ):
                            raise DirectoryError("VERSION_CONFLICT")
                        start = position + 1
                        break
                else:
                    # No position fallback that silently omits or revives records.
                    raise DirectoryError("VERSION_CONFLICT")
            page = matches[start : start + query.limit]
            next_cursor = None
            if start + len(page) < len(matches):
                last = page[-1]
                next_cursor = self._cipher.encrypt(
                    _encoded(
                        [
                            1,
                            self._binding(query),
                            last["public_id"],
                            self._fingerprint(normalized(last["display_name"])),
                        ]
                    )
                ).decode("ascii")
            return _encoded({"items": page, "next_cursor": next_cursor, "order": "display_name"})

    def detail(self, identifier: str) -> bytes:
        identifier = public_uuid(identifier)
        if self.source is None:
            raise DirectoryError("OPERATION_UNAVAILABLE")
        with self.source.eligible_publications() as entries:
            for item in self._publications(entries):
                if item["public_id"] == identifier:
                    return _encoded({"professional": item})
            raise DirectoryError("RESOURCE_UNAVAILABLE")
