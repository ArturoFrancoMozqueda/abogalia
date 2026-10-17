"""Active HTTP validation bound to a verified token; no positive cache or fallback."""

from datetime import UTC, datetime
from uuid import UUID

from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider
from abogalia_api.identity.security import InvalidToken, JWTVerifier, VerificationUnavailable


class ApiSessionProbe:
    def __init__(self, settings, provider=None, clock=None):
        if settings.project_url != "https://spohytnxscljtitvmdab.supabase.co":
            raise StorageUnavailable
        self._provider = provider or SupabaseProvider(settings)
        self._clock = clock or (lambda: datetime.now(UTC))
        self._verifier = JWTVerifier(settings, self._provider.jwks)

    def active(self, provider_session_id: str, subject: str, *, access_token: str) -> bool:
        try:
            if any(
                not isinstance(value, str) or str(UUID(value)) != value or UUID(value).int == 0
                for value in (provider_session_id, subject)
            ):
                raise StorageUnavailable
            identity = self._verifier.verify(access_token, self._clock())
            if identity.subject != subject or identity.provider_session_id != provider_session_id:
                raise StorageUnavailable
            actual = self._provider.session_subject(access_token)
            if actual is None:
                return False
            if actual != subject:
                raise StorageUnavailable
            return True
        except (InvalidToken, VerificationUnavailable, ProviderFailure, ValueError, TypeError):
            raise StorageUnavailable from None
