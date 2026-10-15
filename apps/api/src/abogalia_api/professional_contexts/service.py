"""Own inactive professional aggregate, on Identity's protected business unit."""

from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.service import AuthError
from abogalia_api.professional_contexts.domain import DomainError, DraftFields
from abogalia_api.professional_contexts.storage import PostgresProfessionalContextStore

MESSAGES = {
    "RESOURCE_UNAVAILABLE": "No se encontró un recurso disponible.",
    "VERSION_CONFLICT": "La información cambió. Actualiza antes de continuar.",
    "STATE_CONFLICT": "No es posible realizar esta acción en el estado actual.",
    "PROFESSIONAL_UNAVAILABLE": "La operación no está disponible temporalmente.",
    "INVALID_REQUEST": "Revisa los datos de la solicitud.",
}


class ProfessionalError(Exception):
    def __init__(self, code):
        self.code = code if code in MESSAGES else "PROFESSIONAL_UNAVAILABLE"
        self.status = {
            "RESOURCE_UNAVAILABLE": 404,
            "VERSION_CONFLICT": 409,
            "STATE_CONFLICT": 409,
            "INVALID_REQUEST": 422,
        }.get(self.code, 503)
        super().__init__("Professional operation unavailable")

    def body(self):
        return {"error": {"code": self.code, "message": MESSAGES[self.code]}}


def view(aggregate):
    if aggregate is None:
        return {"profile": None, "practice_context": None}
    profile, practice = aggregate.profile, aggregate.practice
    return {
        "profile": {
            "id": str(profile.profile_id),
            "version": profile.profile_version,
            "state": profile.state,
            "fields": {
                "display_name": profile.fields.display_name,
                "declared_area": profile.fields.declared_area,
            },
            "publication": "private",
            "review": None,
            "allowed_actions": ["edit", "withdraw"] if profile.state == "draft" else [],
        },
        "practice_context": {
            "id": str(practice.context_id),
            "version": practice.context_version,
            "kind": "practice",
            "title": profile.fields.display_name,
            "state": practice.state,
            "capabilities": [],
            "allowed_actions": [],
        },
    }


class ProfessionalService:
    def __init__(self, identity, store_factory=PostgresProfessionalContextStore):
        self.identity = identity
        self._store_factory = store_factory

    def execute(self, reference, operation, payload=None):
        try:
            with self.identity.authenticated(reference, touch=True, business=True) as (
                record,
                conn,
            ):
                if record.assurance != "aal2":
                    raise AuthError(403, "MFA_REQUIRED")
                if operation == "gated":
                    raise AuthError(403, "FEATURE_UNAVAILABLE")
                store = self._store_factory(conn, subject=record.subject, clock=self.identity.clock)
                if operation == "read":
                    return view(store.read())
                if operation == "create":
                    return view(store.create(DraftFields(**payload)))
                if operation == "edit":
                    current = store.read()
                    if current is None:
                        raise ProfessionalError("RESOURCE_UNAVAILABLE")
                    fields = {
                        "display_name": current.profile.fields.display_name,
                        "declared_area": current.profile.fields.declared_area,
                    }
                    fields.update(payload["fields"])
                    return view(
                        store.edit(
                            DraftFields(**fields), expected_version=payload["expected_version"]
                        )
                    )
                if operation == "withdraw":
                    return view(store.withdraw(**payload))
                if operation == "contexts":
                    if payload.get("cursor") is not None:
                        raise ProfessionalError("INVALID_REQUEST")
                    own = view(store.read())["practice_context"]
                    return {"contexts": [own] if own is not None else [], "next_cursor": None}
                raise AuthError(403, "FEATURE_UNAVAILABLE")
        except DomainError as error:
            raise ProfessionalError(error.code) from None
        except StorageUnavailable:
            raise ProfessionalError("PROFESSIONAL_UNAVAILABLE") from None
        except AuthError as error:
            if error.status == 503:
                raise ProfessionalError("PROFESSIONAL_UNAVAILABLE") from None
            raise
