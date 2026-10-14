"""Shared implementation contracts; no provider or storage shortcuts."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class StorageUnavailable(Exception):
    """No database diagnostic or sensitive record is attached."""


@dataclass(repr=False)
class SessionRecord:
    digest: str
    subject: str
    email: str
    provider_session_id: str
    access_token: str
    refresh_token: str
    assurance: str
    created_at: datetime
    last_activity_at: datetime
    token_expires_at: datetime


class SessionTransaction(Protocol):
    record: SessionRecord | None

    def save(self, record: SessionRecord) -> None: ...

    def delete(self) -> None: ...

    def revoke_subject(self, subject: str) -> None: ...


class SessionStore(Protocol):
    def create(self, record: SessionRecord) -> None: ...

    def transaction(self, digest: str) -> AbstractContextManager[SessionTransaction]: ...

    def revoke_subject(self, subject: str) -> None: ...


class SessionProbe(Protocol):
    def active(self, provider_session_id: str, subject: str, *, access_token: str) -> bool: ...


Clock = Callable[[], datetime]
