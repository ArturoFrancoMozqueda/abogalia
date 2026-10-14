"""Session orchestration. All persistent authorization uses injected store/probe."""

import hmac
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from threading import Lock
from uuid import UUID

from abogalia_api.identity.config import Settings
from abogalia_api.identity.contracts import SessionRecord, StorageUnavailable
from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider
from abogalia_api.identity.security import (
    CSRF,
    InvalidToken,
    JWTVerifier,
    VerificationUnavailable,
    digest_reference,
    random_reference,
    valid_reference,
)

MESSAGES = {
    "AUTHENTICATION_REQUIRED": "Se requiere iniciar sesión.",
    "INVALID_CREDENTIALS": "No fue posible iniciar sesión.",
    "INVALID_CODE": "El código no es válido o expiró.",
    "REQUEST_FORBIDDEN": "La solicitud no está permitida.",
    "MFA_REQUIRED": "Completa la verificación adicional.",
    "FEATURE_UNAVAILABLE": "Esta función aún no está disponible.",
    "INVALID_REQUEST": "Revisa los datos de la solicitud.",
    "RATE_LIMITED": "Inténtalo de nuevo más tarde.",
    "AUTH_UNAVAILABLE": "El acceso no está disponible temporalmente.",
}


class AuthError(Exception):
    def __init__(self, status: int, code: str, clear_cookies: bool = False):
        self.status = status
        self.code = code
        self.clear_cookies = clear_cookies
        super().__init__("Identity operation failed")

    def body(self):
        return {"error": {"code": self.code, "message": MESSAGES[self.code]}}


def unavailable():
    return AuthError(503, "AUTH_UNAVAILABLE")


class IdentityService:
    def __init__(self, settings, store=None, probe=None, provider=None, clock=None):
        self.settings: Settings = settings
        self.store = store
        self.probe = probe
        self.provider = provider or SupabaseProvider(settings)
        self.clock = clock or (lambda: datetime.now(UTC))
        self.csrf = CSRF(settings.csrf_key)
        self.verifier = JWTVerifier(settings, self.provider.jwks)
        # Preauthentication contains no identity or provider tokens. Process-local,
        # bounded and fail-closed on worker changes. Authenticated state is SQL-only.
        self._preauth: dict[str, datetime] = {}
        self._challenges: dict[str, tuple[str, str, datetime]] = {}
        self._lock = Lock()

    def require_dependencies(self):
        if not self.settings.configured or self.store is None or self.probe is None:
            raise unavailable()

    def _map_failure(self, failure: ProviderFailure, rejection="INVALID_CREDENTIALS"):
        if failure.kind == "limited":
            return AuthError(429, "RATE_LIMITED")
        if failure.kind in ("weak", "invalid_request"):
            return AuthError(422, "INVALID_REQUEST")
        if failure.kind == "rejected":
            return AuthError(401, rejection)
        return unavailable()

    def _alive(self, record, now):
        return timedelta(0) <= now - record.created_at < timedelta(hours=12) and timedelta(
            0
        ) <= now - record.last_activity_at < timedelta(minutes=30)

    @contextmanager
    def _transaction(self, reference):
        if not valid_reference(reference):
            raise AuthError(401, "AUTHENTICATION_REQUIRED", True)
        if self.store is None:
            raise unavailable()
        try:
            with self.store.transaction(digest_reference(reference)) as tx:
                yield tx
        except StorageUnavailable:
            raise unavailable() from None

    def _preauth_valid(self, reference):
        if not valid_reference(reference):
            return False
        now = self.clock()
        with self._lock:
            expiry = self._preauth.get(digest_reference(reference))
            return expiry is not None and now < expiry

    def _forget_preauth(self, reference):
        if valid_reference(reference):
            with self._lock:
                self._preauth.pop(digest_reference(reference), None)

    def reference_kind(self, reference):
        if self._preauth_valid(reference):
            return "preauth"
        with self._transaction(reference) as tx:
            valid = tx.record is not None and self._alive(tx.record, self.clock())
            if not valid:
                tx.delete()
        # Commit expiration cleanup (including SQL store's automatic deletion)
        # before throwing, otherwise the context manager would roll it back.
        if not valid:
            raise AuthError(401, "AUTHENTICATION_REQUIRED", True)
        return "session"

    def csrf_bootstrap(self, reference, current_token):
        if not self.settings.configured:
            raise unavailable()
        try:
            kind = self.reference_kind(reference)
        except AuthError as exc:
            if exc.status != 401:
                raise
            reference = random_reference()
            now = self.clock()
            with self._lock:
                self._preauth = {k: v for k, v in self._preauth.items() if v > now}
                if len(self._preauth) >= 10000:
                    raise AuthError(429, "RATE_LIMITED") from None
                self._preauth[digest_reference(reference)] = now + timedelta(minutes=30)
            kind = "preauth"
        token = (
            current_token
            if self.csrf.valid(current_token, reference, kind)
            else (self.csrf.create(reference, kind))
        )
        if kind == "preauth":
            with self._lock:
                expiry = self._preauth[digest_reference(reference)]
            remaining = int((expiry - self.clock()).total_seconds())
        else:
            with self._transaction(reference) as tx:
                if tx.record is None:
                    raise AuthError(401, "AUTHENTICATION_REQUIRED", True)
                expiry = tx.record.created_at + timedelta(hours=12)
                remaining = int((expiry - self.clock()).total_seconds())
        return reference, token, max(0, remaining)

    def validate_csrf(self, reference, cookie_token, header_token):
        if not self.settings.configured:
            raise unavailable()
        try:
            kind = self.reference_kind(reference)
        except AuthError as exc:
            if exc.status == 401:
                raise AuthError(403, "REQUEST_FORBIDDEN", exc.clear_cookies) from None
            raise
        if (
            not cookie_token
            or not header_token
            or len(header_token) > 128
            or len(cookie_token) > 128
            or not hmac.compare_digest(cookie_token.encode(), header_token.encode())
            or not self.csrf.valid(header_token, reference, kind)
        ):
            raise AuthError(403, "REQUEST_FORBIDDEN")

    def _validate_tokens(
        self, tokens, *, expected_subject=None, expected_session=None, check_active=True
    ):
        try:
            identity = self.verifier.verify(tokens.access_token, self.clock())
            if (
                identity.subject != tokens.subject
                or (expected_subject is not None and identity.subject != expected_subject)
                or (
                    expected_session is not None
                    and identity.provider_session_id != expected_session
                )
            ):
                raise InvalidToken()
        except (InvalidToken, VerificationUnavailable, StorageUnavailable):
            raise unavailable() from None
        if not check_active:
            return identity
        try:
            if not self.probe.active(
                identity.provider_session_id, identity.subject, access_token=tokens.access_token
            ):
                raise ProviderFailure("rejected")
        except StorageUnavailable:
            raise unavailable() from None
        return identity

    def _active_record(self, record, now):
        try:
            identity = self.verifier.verify(record.access_token, now)
            if (
                identity.subject != record.subject
                or identity.provider_session_id != record.provider_session_id
                or identity.assurance != record.assurance
            ):
                return False
        except InvalidToken:
            return False
        except VerificationUnavailable:
            raise StorageUnavailable from None
        return self.probe.active(
            record.provider_session_id, record.subject, access_token=record.access_token
        )

    def login(self, reference, email, password):
        self.require_dependencies()
        started = self.clock()  # Must precede provider call / global-revocation cutoff.
        try:
            tokens = self.provider.login(email, password)
            identity = self._validate_tokens(tokens)
        except ProviderFailure as exc:
            raise self._map_failure(exc) from None
        new_reference = random_reference()
        record = SessionRecord(
            digest=digest_reference(new_reference),
            subject=identity.subject,
            email=tokens.email,
            provider_session_id=identity.provider_session_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            assurance=identity.assurance,
            created_at=started,
            last_activity_at=started,
            token_expires_at=identity.expires_at,
        )
        try:
            self.store.create(record)
            if valid_reference(reference) and not self._preauth_valid(reference):
                with self._transaction(reference) as tx:
                    tx.delete()
        except StorageUnavailable:
            raise unavailable() from None
        self._forget_preauth(reference)
        return new_reference, self.view(record)

    @staticmethod
    def view(record):
        return {
            "authenticated": True,
            "user": {
                "id": record.subject,
                "email": record.email,
                "assurance": record.assurance,
            },
        }

    @contextmanager
    def authenticated(self, reference, *, touch=False, revoke=False):
        self.require_dependencies()
        pending_error = None
        infrastructure_error = None
        completed = False
        with self._transaction(reference) as tx:
            record = tx.record
            original_digest = record.digest if record is not None else None
            now = self.clock()
            if record is None or not self._alive(record, now):
                tx.delete()
                # Do not raise within transaction: deletion must commit first.
                result = None
            else:
                try:
                    if record.token_expires_at <= now + timedelta(seconds=30):
                        tokens = self.provider.refresh(record.refresh_token)
                        identity = self._validate_tokens(
                            tokens,
                            expected_subject=record.subject,
                            expected_session=record.provider_session_id,
                            check_active=False,
                        )
                        record = replace(
                            record,
                            access_token=tokens.access_token,
                            refresh_token=tokens.refresh_token,
                            email=tokens.email,
                            assurance=identity.assurance,
                            token_expires_at=identity.expires_at,
                        )
                        tx.save(record)
                    if not self._active_record(record, self.clock()):
                        raise InvalidToken()
                    result = record
                except InvalidToken:
                    tx.delete()
                    result = None
                except (VerificationUnavailable, StorageUnavailable):
                    infrastructure_error = unavailable()
                    result = None
                except ProviderFailure as exc:
                    if exc.kind == "rejected":
                        # A definitive refresh rejection purges custodied tokens;
                        # commit deletion before raising authorization failure.
                        tx.delete()
                        result = None
                    else:
                        raise self._map_failure(exc, "AUTHENTICATION_REQUIRED") from None
            if result is not None:
                try:
                    yield result, tx
                except Exception as exc:
                    pending_error = exc
                # External Auth revocation/time can change while a provider call
                # runs, even with a local SQL row lock. Check the result frontier.
                current = tx.record
                try:
                    valid = (
                        current is not None
                        and self._alive(current, self.clock())
                        and current.token_expires_at > self.clock()
                        and self._active_record(current, self.clock())
                    )
                except StorageUnavailable:
                    infrastructure_error = unavailable()
                    valid = None
                if valid:
                    completed = True
                    if pending_error is None:
                        # A failed action must not extend inactivity. Renewal has
                        # already been saved without changing activity; commit it
                        # even if the action later failed, since Auth consumed the
                        # previous refresh token.
                        if touch:
                            current = replace(current, last_activity_at=self.clock())
                            tx.save(current)
                        if revoke:
                            # Global logout finalizer runs after both checks and
                            # commits local revocation before external signout.
                            tx.revoke_subject(current.subject)
                elif valid is False:
                    tx.delete()
                elif current is not None and current.digest != original_digest:
                    # MFA consumed/rotated credentials, but no new cookie can be
                    # delivered on 503. Preserve the existing opaque reference.
                    tx.save(replace(current, digest=original_digest))
        # Raising inside the SQL context would roll back a necessary refresh.
        if infrastructure_error is not None:
            raise infrastructure_error from None
        if completed:
            if pending_error is not None:
                raise pending_error from None
            return
        raise AuthError(401, "AUTHENTICATION_REQUIRED", True)

    def session(self, reference):
        if not valid_reference(reference) or self._preauth_valid(reference):
            return {"authenticated": False}
        try:
            with self.authenticated(reference) as (record, _):
                return self.view(record)
        except AuthError as exc:
            if exc.status == 401:
                return {"authenticated": False}
            raise

    def logout(self, reference, scope):
        if self._preauth_valid(reference):
            if scope == "global":
                raise AuthError(401, "AUTHENTICATION_REQUIRED")
            self._forget_preauth(reference)
            return
        self.require_dependencies()
        if scope == "global":
            # A revoked Auth cookie must not authorize removing newer sessions.
            # authenticated validates before yielding and at the result frontier;
            # its trusted finalizer revokes under the same subject/row locks.
            with self.authenticated(reference, revoke=True) as (record, _):
                access = record.access_token
        else:
            with self._transaction(reference) as tx:
                record = tx.record
                if record is None:
                    return
                access = record.access_token
                tx.delete()
        # Revocation committed before external failure, never rolled back.
        try:
            self.provider.logout(access, scope)
        except ProviderFailure:
            raise AuthError(503, "AUTH_UNAVAILABLE", True) from None

    def email_operation(self, operation, email, password=None):
        if not self.settings.configured or not self.settings.email_enabled:
            raise unavailable()
        try:
            if operation == "register":
                self.provider.register(email, password)
            else:
                self.provider.recover(email)
        except ProviderFailure as exc:
            if exc.kind in ("duplicate", "unknown"):
                # Only explicit known existence outcomes are normalized.
                return
            if exc.kind in ("weak", "invalid_request", "limited"):
                raise self._map_failure(exc) from None
            raise unavailable() from None

    def confirm(self, email, code):
        self.require_dependencies()
        if not self.settings.email_enabled:
            raise unavailable()
        try:
            tokens = self.provider.verify_code(email, code, "email")
            self._validate_tokens(tokens)
            self.provider.logout(tokens.access_token, "local")
        except ProviderFailure as exc:
            raise self._map_failure(exc, "INVALID_CODE") from None

    def complete_recovery(self, email, code, password):
        self.require_dependencies()
        if not self.settings.email_enabled:
            raise unavailable()
        try:
            tokens = self.provider.verify_code(email, code, "recovery")
        except ProviderFailure as exc:
            raise self._map_failure(exc, "INVALID_CODE") from None
        try:
            identity = self._validate_tokens(tokens)
        except ProviderFailure as exc:
            raise self._map_failure(exc, "INVALID_CODE") from None
        try:
            self.provider.update_password(tokens.access_token, password)
        except ProviderFailure as exc:
            if exc.kind in ("weak", "invalid_request"):
                raise AuthError(422, "INVALID_REQUEST") from None
            raise self._map_failure(exc, "INVALID_CODE") from None
        try:
            self.store.revoke_subject(identity.subject)
        except StorageUnavailable:
            raise AuthError(503, "AUTH_UNAVAILABLE", True) from None
        try:
            self.provider.logout(tokens.access_token, "global")
        except ProviderFailure:
            raise AuthError(503, "AUTH_UNAVAILABLE", True) from None

    @staticmethod
    def _uuid(value):
        try:
            return isinstance(value, str) and str(UUID(value)) == value
        except (ValueError, TypeError, AttributeError):
            return False

    def _factors(self, record):
        factors = self.provider.factors(record.access_token)
        result = []
        for factor in factors:
            if not isinstance(factor, dict) or factor.get("factor_type") != "totp":
                continue
            if self._uuid(factor.get("id")) and factor.get("status") in ("verified", "unverified"):
                result.append({"id": factor["id"], "status": factor["status"]})
        return result

    def mfa(self, operation, reference, body):
        try:
            with self.authenticated(reference, touch=operation != "factors") as (record, tx):
                factors = self._factors(record)
                if operation == "factors":
                    return {"factors": factors}, None
                if operation == "enroll":
                    data = self.provider.enroll(record.access_token)
                    totp = data.get("totp", {})
                    if not self._uuid(data.get("id")) or not all(
                        isinstance(totp.get(key), str) and 0 < len(totp[key]) <= 65536
                        for key in ("qr_code", "secret", "uri")
                    ):
                        raise unavailable()
                    return {
                        "factor_id": data["id"],
                        "totp": {key: totp[key] for key in ("qr_code", "secret", "uri")},
                    }, None
                if body["factor_id"] not in [f["id"] for f in factors]:
                    raise AuthError(403, "REQUEST_FORBIDDEN")
                if operation == "challenge":
                    data = self.provider.challenge(record.access_token, body["factor_id"])
                    if not self._uuid(data.get("id")) or type(data.get("expires_at")) is not int:
                        raise unavailable()
                    expiry = datetime.fromtimestamp(data["expires_at"], tz=UTC)
                    now = self.clock()
                    if expiry <= now:
                        raise unavailable()
                    with self._lock:
                        self._challenges = {
                            key: value for key, value in self._challenges.items() if value[2] > now
                        }
                        if len(self._challenges) >= 10000:
                            raise AuthError(429, "RATE_LIMITED")
                        self._challenges[data["id"]] = (
                            record.provider_session_id,
                            body["factor_id"],
                            expiry,
                        )
                    return {"challenge_id": data["id"], "expires_at": data["expires_at"]}, None
                with self._lock:
                    bound = self._challenges.get(body["challenge_id"])
                    if (
                        bound is None
                        or bound[0] != record.provider_session_id
                        or bound[1] != body["factor_id"]
                        or bound[2] <= self.clock()
                    ):
                        raise AuthError(403, "REQUEST_FORBIDDEN")
                    # Consume before provider request, including failed attempts.
                    self._challenges.pop(body["challenge_id"])
                tokens = self.provider.verify_mfa(
                    record.access_token,
                    body["factor_id"],
                    body["challenge_id"],
                    body["code"],
                    subject=record.subject,
                    email=record.email,
                )
                identity = self._validate_tokens(
                    tokens,
                    expected_subject=record.subject,
                    expected_session=record.provider_session_id,
                    check_active=False,
                )
                if identity.assurance != "aal2":
                    raise unavailable()
                new_reference = random_reference()
                elevated = replace(
                    record,
                    digest=digest_reference(new_reference),
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                    assurance="aal2",
                    email=tokens.email,
                    token_expires_at=identity.expires_at,
                )
                # Atomic rotation, preserving absolute lifetime under the SQL lock.
                tx.save(elevated)
                response = self.view(elevated)
            return response, new_reference
        except ProviderFailure as exc:
            raise self._map_failure(exc, "INVALID_CODE") from None
