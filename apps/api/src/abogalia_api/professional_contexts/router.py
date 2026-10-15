"""Strict private first increment. Closed families never return fake success."""

from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from abogalia_api.identity.service import AuthError
from abogalia_api.professional_contexts.service import ProfessionalError
from abogalia_api.routes.auth import ErrorView, clear_cookies


class Body(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)

    def __repr_args__(self):
        return []


class Fields(Body):
    display_name: Annotated[str, Field(min_length=1, max_length=120)]
    declared_area: Annotated[str | None, Field(max_length=240)] = None


class PartialFields(Body):
    display_name: Annotated[str, Field(min_length=1, max_length=120)] = None
    declared_area: Annotated[str | None, Field(max_length=240)] = None

    @model_validator(mode="after")
    def nonempty(self):
        if not self.model_fields_set:
            raise ValueError("Invalid request")
        return self


Version = Annotated[int, Field(gt=0, le=2**31 - 1)]


class Edit(Body):
    expected_version: Version
    fields: PartialFields


class Withdraw(Body):
    expected_version: Version
    expected_context_version: Version


class ProfileView(Body):
    id: str
    version: int
    state: Literal["draft", "withdrawn"]
    fields: Fields
    publication: Literal["private"]
    review: None
    allowed_actions: list[Literal["edit", "withdraw"]]


class ContextView(Body):
    id: str
    version: int
    kind: Literal["practice"]
    title: str
    state: Literal["preparing", "closed"]
    capabilities: list[str]
    allowed_actions: list[str]


class OwnView(Body):
    profile: ProfileView | None
    practice_context: ContextView | None


class ContextList(Body):
    contexts: list[ContextView]
    next_cursor: None


def error_response(error, settings):
    response = JSONResponse(error.body(), status_code=error.status)
    if isinstance(error, AuthError) and error.clear_cookies:
        clear_cookies(response, settings)
    return response


class ProtectedRoute(APIRoute):
    def get_route_handler(self):
        endpoint = super().get_route_handler()

        async def handle(request):
            identity = request.app.state.identity
            try:
                if request.headers.get("authorization") is not None:
                    raise AuthError(403, "REQUEST_FORBIDDEN")
                if request.url.query:
                    allowed = (
                        request.method == "GET" and request.url.path == "/api/professional/contexts"
                    )
                    pairs = request.query_params.multi_items()
                    if (
                        not allowed
                        or any(name not in ("cursor", "limit") for name, _ in pairs)
                        or len({name for name, _ in pairs}) != len(pairs)
                    ):
                        raise AuthError(403, "REQUEST_FORBIDDEN")
                payload = bytearray()
                async for chunk in request.stream():
                    if len(payload) + len(chunk) > 8192:
                        raise AuthError(422, "INVALID_REQUEST")
                    payload.extend(chunk)
                request._body = bytes(payload)
                if request.method == "GET" and payload:
                    raise AuthError(422, "INVALID_REQUEST")
                if request.method in ("POST", "PATCH"):
                    if (
                        len(request.headers.getlist("origin")) != 1
                        or request.headers.get("origin") != identity.settings.origin
                        or len(request.headers.getlist("x-csrf-token")) != 1
                    ):
                        raise AuthError(403, "REQUEST_FORBIDDEN")
                    if request.headers.get("content-type", "").split(";")[0] != "application/json":
                        raise AuthError(422, "INVALID_REQUEST")
                    await run_in_threadpool(
                        identity.validate_csrf,
                        request.cookies.get(identity.settings.session_cookie),
                        request.cookies.get(identity.settings.csrf_cookie),
                        request.headers.get("x-csrf-token"),
                    )
                response = await endpoint(request)
            except RequestValidationError:
                response = error_response(AuthError(422, "INVALID_REQUEST"), identity.settings)
            except (AuthError, ProfessionalError) as error:
                response = error_response(error, identity.settings)
            except Exception:
                response = error_response(
                    ProfessionalError("PROFESSIONAL_UNAVAILABLE"), identity.settings
                )
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
            return response

        return handle


router = APIRouter(
    prefix="/api/professional",
    tags=["Professional contexts"],
    route_class=ProtectedRoute,
    responses={status: {"model": ErrorView} for status in (401, 403, 404, 409, 422, 429, 503)},
)


def invoke(request, operation, payload=None):
    reference = request.cookies.get(request.app.state.identity.settings.session_cookie)
    return request.app.state.professional.execute(reference, operation, payload)


@router.get("/profile", response_model=OwnView)
def read_profile(request: Request):
    return invoke(request, "read")


@router.post("/profile", response_model=OwnView, status_code=201)
def create_profile(request: Request, body: Fields):
    return invoke(request, "create", body.model_dump())


@router.patch("/profile", response_model=OwnView)
def edit_profile(request: Request, body: Edit):
    return invoke(
        request,
        "edit",
        {
            "expected_version": body.expected_version,
            "fields": body.fields.model_dump(exclude_unset=True),
        },
    )


@router.post("/profile/withdraw", response_model=OwnView)
def withdraw_profile(request: Request, body: Withdraw):
    return invoke(request, "withdraw", body.model_dump())


@router.get("/contexts", response_model=ContextList)
def list_contexts(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: Annotated[str | None, Query(max_length=200)] = None,
):
    return invoke(request, "contexts", {"limit": limit, "cursor": cursor})


@router.api_route("/{closed_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
def gated(request: Request, closed_path: str):
    return invoke(request, "gated")
