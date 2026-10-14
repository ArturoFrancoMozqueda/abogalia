"""GoTrue gateway: public project key, private session bearer, no diagnostic bodies."""

import json
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

import httpx

from abogalia_api.identity.config import Settings


class ProviderFailure(Exception):
    def __init__(self, kind: str = "unavailable"):
        self.kind = kind
        super().__init__("Identity provider operation failed")


@dataclass(frozen=True, repr=False)
class ProviderTokens:
    access_token: str
    refresh_token: str
    subject: str
    email: str


class Provider(Protocol):
    def jwks(self) -> dict: ...
    def session_subject(self, access_token: str) -> str | None: ...
    def login(self, email: str, password: str) -> ProviderTokens: ...
    def refresh(self, refresh_token: str) -> ProviderTokens: ...
    def logout(self, access_token: str, scope: str) -> None: ...
    def register(self, email: str, password: str) -> None: ...
    def recover(self, email: str) -> None: ...
    def verify_code(self, email: str, code: str, kind: str) -> ProviderTokens: ...
    def update_password(self, access_token: str, password: str) -> None: ...
    def factors(self, access_token: str) -> list[dict]: ...
    def enroll(self, access_token: str) -> dict: ...
    def challenge(self, access_token: str, factor: str) -> dict: ...
    def verify_mfa(
        self, access_token: str, factor: str, challenge: str, code: str, *, subject: str, email: str
    ) -> ProviderTokens: ...


class SupabaseProvider:
    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self.settings = settings
        self.client = client or httpx.Client(timeout=10, follow_redirects=False, trust_env=False)

    def _request(self, method: str, path: str, *, payload=None, token=None, params=None):
        if not self.settings.configured:
            raise ProviderFailure()
        headers = {"apikey": self.settings.publishable_key}
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        try:
            response = self.client.request(
                method, self.settings.issuer + path, headers=headers, json=payload, params=params
            )
            if response.status_code == 429:
                raise ProviderFailure("limited")
            if response.status_code in (400, 401, 403, 422):
                # Only allowlisted codes are retained as fixed internal categories.
                # Never attach response content/messages or arbitrary codes to errors.
                if len(response.content) > 8192:
                    raise ProviderFailure()
                error = response.json()
                code = (
                    error.get("code", error.get("error_code")) if isinstance(error, dict) else None
                )
                category = (
                    {
                        "user_already_exists": "duplicate",
                        "email_exists": "duplicate",
                        "user_not_found": "unknown",
                        "weak_password": "weak",
                        "email_address_invalid": "invalid_request",
                        "same_password": "invalid_request",
                        "invalid_credentials": "rejected",
                        "email_not_confirmed": "rejected",
                        "otp_expired": "rejected",
                        "refresh_token_not_found": "rejected",
                        "refresh_token_already_used": "rejected",
                        "session_not_found": "rejected",
                        "session_expired": "rejected",
                        "bad_jwt": "rejected",
                        "mfa_challenge_expired": "rejected",
                        "mfa_factor_not_found": "rejected",
                        "mfa_verification_failed": "rejected",
                        "mfa_verification_rejected": "rejected",
                    }.get(code, "unavailable")
                    if isinstance(code, str)
                    else "unavailable"
                )
                raise ProviderFailure(category)
            if response.status_code not in (200, 201, 204):
                raise ProviderFailure()
            if response.status_code == 204:
                return {}
            if len(response.content) > 131072:
                raise ProviderFailure()
            result = response.json()
            if not isinstance(result, dict):
                raise ProviderFailure()
            return result
        except ProviderFailure:
            raise
        except Exception:
            raise ProviderFailure() from None

    def session_subject(self, access_token: str) -> str | None:
        """One bounded isolated request; only allowlisted absence codes prove revocation."""
        if (
            self.settings.project_url != "https://spohytnxscljtitvmdab.supabase.co"
            or not self.settings.configured
            or not isinstance(access_token, str)
            or not 0 < len(access_token) <= 16384
        ):
            raise ProviderFailure()
        response = None
        try:
            request = httpx.Request(
                "GET",
                self.settings.issuer + "/user",
                headers={
                    "apikey": self.settings.publishable_key,
                    "Authorization": "Bearer " + access_token,
                },
                extensions={"timeout": httpx.Timeout(10).as_dict()},
            )
            response = self.client.send(request, stream=True, follow_redirects=False)
            if response.status_code not in (200, 401, 403) or response.headers.get(
                "content-encoding", "identity"
            ) not in ("", "identity"):
                raise ProviderFailure()
            payload = bytearray()
            bound = 8192 if response.status_code in (401, 403) else 65536
            for chunk in response.iter_bytes():
                if len(payload) + len(chunk) > bound:
                    raise ProviderFailure()
                payload.extend(chunk)
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ProviderFailure()
            if response.status_code in (401, 403):
                code = data.get("code", data.get("error_code"))
                if code in ("session_not_found", "user_not_found"):
                    return None
                raise ProviderFailure()
            subject = data.get("id")
            if (
                not isinstance(subject, str)
                or str(UUID(subject)) != subject
                or UUID(subject).int == 0
            ):
                raise ProviderFailure()
            return subject
        except Exception:
            raise ProviderFailure() from None
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    raise ProviderFailure() from None

    @staticmethod
    def _tokens(data: dict) -> ProviderTokens:
        try:
            user = data["user"]
            email, subject = user["email"], user["id"]
            if not user.get("email_confirmed_at"):
                raise ProviderFailure("rejected")
            if not isinstance(email, str) or "@" not in email or len(email) > 254:
                raise ProviderFailure()
            if str(UUID(subject)) != subject:
                raise ProviderFailure()
            access, refresh = data["access_token"], data["refresh_token"]
            if not all(isinstance(t, str) and 0 < len(t) <= 16384 for t in (access, refresh)):
                raise ProviderFailure()
            return ProviderTokens(access, refresh, subject, email)
        except ProviderFailure:
            raise
        except (KeyError, TypeError, ValueError):
            raise ProviderFailure() from None

    def jwks(self) -> dict:
        return self._request("GET", "/.well-known/jwks.json")

    def login(self, email: str, password: str) -> ProviderTokens:
        return self._tokens(
            self._request(
                "POST",
                "/token",
                payload={"email": email, "password": password},
                params={"grant_type": "password"},
            )
        )

    def refresh(self, refresh_token: str) -> ProviderTokens:
        return self._tokens(
            self._request(
                "POST",
                "/token",
                payload={"refresh_token": refresh_token},
                params={"grant_type": "refresh_token"},
            )
        )

    def logout(self, access_token: str, scope: str) -> None:
        self._request("POST", "/logout", token=access_token, params={"scope": scope})

    def _email(self):
        if not self.settings.email_enabled:
            raise ProviderFailure()

    def register(self, email: str, password: str) -> None:
        self._email()
        self._request("POST", "/signup", payload={"email": email, "password": password})

    def recover(self, email: str) -> None:
        self._email()
        self._request("POST", "/recover", payload={"email": email})

    def verify_code(self, email: str, code: str, kind: str) -> ProviderTokens:
        self._email()
        return self._tokens(
            self._request("POST", "/verify", payload={"email": email, "token": code, "type": kind})
        )

    def update_password(self, access_token: str, password: str) -> None:
        self._request("PUT", "/user", token=access_token, payload={"password": password})

    def factors(self, access_token: str) -> list[dict]:
        data = self._request("GET", "/user", token=access_token)
        factors = data.get("factors", [])
        if not isinstance(factors, list):
            raise ProviderFailure()
        return factors

    def enroll(self, access_token: str) -> dict:
        return self._request(
            "POST", "/factors", token=access_token, payload={"factor_type": "totp"}
        )

    def challenge(self, access_token: str, factor: str) -> dict:
        return self._request("POST", f"/factors/{factor}/challenge", token=access_token, payload={})

    def verify_mfa(
        self, access_token: str, factor: str, challenge: str, code: str, *, subject: str, email: str
    ) -> ProviderTokens:
        # Trusted caller supplies the already verified record identity. No GET
        # can consume a rotated pair before the service persists its custody.
        data = self._request(
            "POST",
            f"/factors/{factor}/verify",
            token=access_token,
            payload={"challenge_id": challenge, "code": code},
        )
        if "user" in data:
            return self._tokens(data)
        access, refresh = data.get("access_token"), data.get("refresh_token")
        if not all(
            isinstance(value, str) and 0 < len(value) <= 16384 for value in (access, refresh)
        ):
            raise ProviderFailure()
        return ProviderTokens(access, refresh, subject, email)
