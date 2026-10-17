"""Minimal Spanish Auth HTTP contract; no SDK models are serialized."""

import re
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator
from starlette.responses import JSONResponse, Response

from abogalia_api.identity.service import AuthError


class Body(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    def __repr_args__(self):
        return []


class ErrorDetail(Body):
    code: str
    message: str


class ErrorView(Body):
    error: ErrorDetail


class AnonymousSession(Body):
    authenticated: Literal[False]


class SessionUser(Body):
    id: str
    email: str
    assurance: Literal["aal1", "aal2"]


class AuthenticatedSession(Body):
    authenticated: Literal[True]
    user: SessionUser


SessionView = AnonymousSession | AuthenticatedSession
SESSION_ADAPTER = TypeAdapter(SessionView)


class CSRFView(Body):
    csrf_token: str


class AcceptedView(Body):
    accepted: Literal[True]


class FactorView(Body):
    id: str
    status: Literal["verified", "unverified"]


class FactorsView(Body):
    factors: list[FactorView]


class TOTPView(Body):
    qr_code: str
    secret: str
    uri: str


class EnrollmentView(Body):
    factor_id: str
    totp: TOTPView


class ChallengeView(Body):
    challenge_id: str
    expires_at: int


COMMON_ERRORS = {status: {"model": ErrorView} for status in (403, 422, 429, 503)}
AUTH_ERRORS = {**COMMON_ERRORS, 401: {"model": ErrorView}}
router = APIRouter(prefix="/api/auth", tags=["Identity"], responses=COMMON_ERRORS)


def session_response(data):
    return JSONResponse(SESSION_ADAPTER.validate_python(data).model_dump())


class Email(Body):
    email: Annotated[str, Field(min_length=3, max_length=254)]

    @field_validator("email")
    @classmethod
    def email_format(cls, value):
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Invalid request")
        return value


class Credentials(Email):
    password: Annotated[str, Field(min_length=1, max_length=1024)]

    @field_validator("password")
    @classmethod
    def password_size(cls, value):
        if len(value.encode("utf-8")) > 1024:
            raise ValueError("Invalid request")
        return value


class Code(Email):
    code: Annotated[str, Field(pattern=r"^[0-9]{6}$")]


class Recovery(Code):
    new_password: Annotated[str, Field(min_length=1, max_length=1024)]

    @field_validator("new_password")
    @classmethod
    def password_size(cls, value):
        return Credentials.password_size(value)


class Logout(Body):
    scope: Literal["local", "global"]


class Factor(Body):
    factor_id: str

    @field_validator("factor_id")
    @classmethod
    def uuid_format(cls, value):
        try:
            if str(UUID(value)) != value:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Invalid request") from None
        return value


class Verification(Factor):
    challenge_id: str
    code: Annotated[str, Field(pattern=r"^[0-9]{6}$")]

    @field_validator("challenge_id")
    @classmethod
    def uuid_format(cls, value):
        return Factor.uuid_format(value)


def clear_cookies(response, settings):
    for name, http_only in ((settings.session_cookie, True), (settings.csrf_cookie, False)):
        response.delete_cookie(
            name,
            path="/",
            httponly=http_only,
            secure=not settings.development_http,
            samesite="strict",
        )


def set_session(response, settings, reference, max_age=43200):
    response.set_cookie(
        settings.session_cookie,
        reference,
        path="/",
        httponly=True,
        secure=not settings.development_http,
        samesite="strict",
        max_age=max_age,
    )


def auth_service(request):
    return request.app.state.identity


def cookie(request):
    return request.cookies.get(auth_service(request).settings.session_cookie)


@router.get("/session", response_model=SessionView)
def session(request: Request):
    service = auth_service(request)
    data = service.session(cookie(request))
    response = session_response(data)
    if not data["authenticated"] and cookie(request):
        # Preserve a legitimate preauthentication reference for form submission.
        if not service._preauth_valid(cookie(request)):
            clear_cookies(response, service.settings)
    return response


@router.get("/csrf", response_model=CSRFView)
def csrf(request: Request):
    service = auth_service(request)
    origin = request.headers.get("origin")
    valid = (
        origin == service.settings.origin
        if origin is not None
        else (
            request.headers.get("sec-fetch-site") == "same-origin"
            and request.headers.get("sec-fetch-mode") in ("cors", "same-origin")
        )
    )
    if not valid:
        raise AuthError(403, "REQUEST_FORBIDDEN")
    reference, token, max_age = service.csrf_bootstrap(
        cookie(request), request.cookies.get(service.settings.csrf_cookie)
    )
    response = JSONResponse(CSRFView(csrf_token=token).model_dump())
    # Authenticated bootstrap must not renew the browser's absolute cookie clock.
    if service._preauth_valid(reference):
        set_session(response, service.settings, reference, max_age)
    response.set_cookie(
        service.settings.csrf_cookie,
        token,
        path="/",
        httponly=False,
        secure=not service.settings.development_http,
        samesite="strict",
        max_age=max_age,
    )
    return response


@router.post("/login", response_model=SessionView, responses=AUTH_ERRORS)
def login(body: Credentials, request: Request):
    service = auth_service(request)
    reference, view = service.login(cookie(request), body.email, body.password)
    response = session_response(view)
    response.delete_cookie(
        service.settings.csrf_cookie,
        path="/",
        secure=not service.settings.development_http,
        samesite="strict",
    )
    set_session(response, service.settings, reference)
    return response


@router.post("/register", status_code=202, response_model=AcceptedView)
def register(body: Credentials, request: Request):
    auth_service(request).email_operation("register", body.email, body.password)
    return {"accepted": True}


@router.post("/recover", status_code=202, response_model=AcceptedView)
def recover(body: Email, request: Request):
    auth_service(request).email_operation("recover", body.email)
    return {"accepted": True}


@router.post("/confirm", status_code=204, response_model=None, responses=AUTH_ERRORS)
def confirm(body: Code, request: Request):
    auth_service(request).confirm(body.email, body.code)
    return Response(status_code=204)


@router.post("/recover/complete", status_code=204, response_model=None, responses=AUTH_ERRORS)
def complete(body: Recovery, request: Request):
    service = auth_service(request)
    service.complete_recovery(body.email, body.code, body.new_password)
    service._forget_preauth(cookie(request))
    response = Response(status_code=204)
    clear_cookies(response, service.settings)
    return response


@router.post("/logout", status_code=204, response_model=None, responses=AUTH_ERRORS)
def logout(body: Logout, request: Request):
    service = auth_service(request)
    service.logout(cookie(request), body.scope)
    response = Response(status_code=204)
    clear_cookies(response, service.settings)
    return response


@router.get("/mfa/factors", response_model=FactorsView, responses=AUTH_ERRORS)
def factors(request: Request):
    result, _ = auth_service(request).mfa("factors", cookie(request), {})
    return result


@router.post("/mfa/enroll", status_code=201, response_model=EnrollmentView, responses=AUTH_ERRORS)
def enroll(body: Body, request: Request):
    result, _ = auth_service(request).mfa("enroll", cookie(request), {})
    return JSONResponse(EnrollmentView.model_validate(result).model_dump(), status_code=201)


@router.post("/mfa/challenge", response_model=ChallengeView, responses=AUTH_ERRORS)
def challenge(body: Factor, request: Request):
    result, _ = auth_service(request).mfa("challenge", cookie(request), body.model_dump())
    return result


@router.post("/mfa/verify", response_model=SessionView, responses=AUTH_ERRORS)
def verify(body: Verification, request: Request):
    service = auth_service(request)
    result, reference = service.mfa("verify", cookie(request), body.model_dump())
    response = session_response(result)
    response.delete_cookie(
        service.settings.csrf_cookie,
        path="/",
        secure=not service.settings.development_http,
        samesite="strict",
    )
    # Rotation never extends absolute max_age; service maintains server clock too.
    with service.authenticated(reference) as (record, _):
        remaining = int((record.created_at.timestamp() + 43200) - service.clock().timestamp())
    set_session(response, service.settings, reference, max(0, remaining))
    return response


@router.post("/mfa/recover", status_code=403, response_model=ErrorView)
@router.post("/mfa/unenroll", status_code=403, response_model=ErrorView)
def disabled(request: Request):
    raise AuthError(403, "FEATURE_UNAVAILABLE")
