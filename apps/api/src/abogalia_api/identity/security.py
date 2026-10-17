"""Bound CSRF tokens and signature/claims verification without sensitive diagnostics."""

import base64
import hashlib
import hmac
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import jwt

from abogalia_api.identity.config import Settings


class InvalidToken(Exception):
    pass


class VerificationUnavailable(Exception):
    pass


def random_reference() -> str:
    return secrets.token_urlsafe(32)


def digest_reference(reference: str) -> str:
    return hashlib.sha256(reference.encode("ascii")).hexdigest()


def valid_reference(reference: str | None) -> bool:
    return bool(reference and re.fullmatch(r"[A-Za-z0-9_-]{43}", reference))


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class CSRF:
    def __init__(self, key: bytes):
        self._key = key

    def _mac(self, reference: str, kind: str, nonce: str) -> str:
        parts = (b"abogalia-csrf-v1", kind.encode(), reference.encode(), nonce.encode())
        message = b"".join(len(part).to_bytes(4, "big") + part for part in parts)
        return _b64(hmac.digest(self._key, message, "sha256"))

    def create(self, reference: str, kind: str) -> str:
        nonce = random_reference()
        return f"v1.{nonce}.{self._mac(reference, kind, nonce)}"

    def valid(self, token: str | None, reference: str, kind: str) -> bool:
        if (
            not self._key
            or not token
            or not re.fullmatch(r"v1\.[A-Za-z0-9_-]{43}\.[A-Za-z0-9_-]{43}", token)
        ):
            return False
        _, nonce, mac = token.split(".")
        return hmac.compare_digest(mac, self._mac(reference, kind, nonce))


@dataclass(frozen=True, repr=False)
class VerifiedIdentity:
    subject: str
    provider_session_id: str
    assurance: str
    expires_at: datetime


class JWTVerifier:
    def __init__(self, settings: Settings, jwks_loader: Callable[[], dict]):
        self.settings = settings
        self.loader = jwks_loader

    def verify(self, token: str, now: datetime) -> VerifiedIdentity:
        try:
            if not isinstance(token, str) or len(token) > 16384:
                raise InvalidToken()
            header = jwt.get_unverified_header(token)
            alg, kid = header.get("alg"), header.get("kid")
            if alg not in ("ES256", "RS256") or not isinstance(kid, str) or not kid:
                raise InvalidToken()
            # Never honor jku/x5u/jwk supplied in a token.
            if any(name in header for name in ("jku", "x5u", "jwk")):
                raise InvalidToken()
        except (jwt.PyJWTError, ValueError, TypeError):
            raise InvalidToken() from None
        try:
            keyset = self.loader()
            keys = keyset.get("keys")
            if not isinstance(keys, list) or len(keys) > 30:
                raise VerificationUnavailable()
            matches = [k for k in keys if isinstance(k, dict) and k.get("kid") == kid]
            if len(matches) != 1:
                raise InvalidToken()
            raw = matches[0]
            if raw.get("use", "sig") != "sig" or raw.get("alg", alg) != alg:
                raise InvalidToken()
            if raw.get("kty") != ("EC" if alg == "ES256" else "RSA"):
                raise InvalidToken()
            key = jwt.PyJWK.from_dict(raw, algorithm=alg).key
            claims = jwt.decode(
                token,
                key,
                algorithms=[alg],
                audience=self.settings.audience,
                issuer=self.settings.issuer,
                options={
                    "require": ["iss", "aud", "exp", "iat", "sub", "session_id", "aal"],
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                },
            )
            exp, issued = claims["exp"], claims["iat"]
            current = now.timestamp()
            if type(exp) is not int or type(issued) is not int:
                raise InvalidToken()
            if exp <= current or issued > current or exp <= issued or exp - issued > 900:
                raise InvalidToken()
            if "nbf" in claims and (type(claims["nbf"]) is not int or claims["nbf"] > current):
                raise InvalidToken()
            subject, session_id = claims["sub"], claims["session_id"]
            if str(UUID(subject)) != subject or str(UUID(session_id)) != session_id:
                raise InvalidToken()
            assurance = claims["aal"]
            if assurance not in ("aal1", "aal2"):
                raise InvalidToken()
            return VerifiedIdentity(
                subject, session_id, assurance, datetime.fromtimestamp(exp, tz=now.tzinfo)
            )
        except (InvalidToken, VerificationUnavailable):
            raise
        except (jwt.PyJWTError, ValueError, TypeError, KeyError, AttributeError):
            raise InvalidToken() from None
        except Exception:
            raise VerificationUnavailable() from None
