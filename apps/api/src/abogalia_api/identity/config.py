"""Explicit runtime injection; never reads dotenv or prints settings."""

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True, repr=False)
class Settings:
    origin: str = "http://127.0.0.1:5190"
    development_http: bool = True
    project_url: str = ""
    publishable_key: str = ""
    csrf_key: bytes = b""
    email_enabled: bool = False
    # Public project destination approved in the service registry.
    audience: str = "authenticated"

    def __post_init__(self):
        origin = urlsplit(self.origin)
        if origin.username or origin.password or origin.query or origin.fragment:
            raise ValueError("Invalid identity configuration")
        if origin.path not in ("", "/") or self.origin.endswith("/"):
            raise ValueError("Invalid identity configuration")
        if self.development_http:
            if self.origin != "http://127.0.0.1:5190":
                raise ValueError("Invalid local identity origin")
        elif origin.scheme != "https" or not origin.hostname:
            raise ValueError("HTTPS identity origin required")
        if self.project_url:
            target = urlsplit(self.project_url)
            if (
                target.username
                or target.password
                or target.query
                or target.fragment
                or target.path not in ("", "/")
                or self.project_url.endswith("/")
            ):
                raise ValueError("Invalid identity destination")
            allowed = (
                target.scheme == "https"
                and target.hostname == "spohytnxscljtitvmdab.supabase.co"
                and target.port is None
            )
            local = (
                self.development_http
                and target.scheme == "http"
                and target.hostname in ("127.0.0.1", "localhost")
            )
            if not (allowed or local):
                raise ValueError("Identity destination is not authorized")
        if self.publishable_key and not self.publishable_key.startswith("sb_publishable_"):
            raise ValueError("Publishable identity key required")
        if not isinstance(self.csrf_key, bytes) or (self.csrf_key and len(self.csrf_key) < 32):
            raise ValueError("CSRF configuration unavailable")

    @property
    def configured(self) -> bool:
        return bool(self.project_url and self.publishable_key and len(self.csrf_key) >= 32)

    @property
    def session_cookie(self) -> str:
        return "abogalia_session" if self.development_http else "__Host-abogalia_session"

    @property
    def csrf_cookie(self) -> str:
        return "abogalia_csrf" if self.development_http else "__Host-abogalia_csrf"

    @property
    def issuer(self) -> str:
        return self.project_url + "/auth/v1"
