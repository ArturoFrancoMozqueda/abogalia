from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from abogalia_api.identity.config import Settings
from abogalia_api.identity.logging import configure_identity_logging
from abogalia_api.identity.runtime import load_runtime
from abogalia_api.identity.service import AuthError, IdentityService
from abogalia_api.routes.auth import clear_cookies
from abogalia_api.routes.auth import router as auth_router
from abogalia_api.routes.health import router as health_router


def create_app(settings=None, store=None, probe=None, provider=None, clock=None) -> FastAPI:
    configure_identity_logging()
    app = FastAPI(title="Abogalia API", version="0.1.0")
    if all(value is None for value in (settings, store, probe, provider, clock)):
        settings, store, probe = load_runtime()
    settings = settings or Settings()
    app.state.identity = IdentityService(settings, store, probe, provider, clock)
    app.include_router(health_router)
    app.include_router(auth_router)

    def error_response(error):
        response = JSONResponse(error.body(), status_code=error.status)
        if error.clear_cookies:
            clear_cookies(response, settings)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(AuthError)
    async def auth_error(request: Request, exc: AuthError):
        return error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return error_response(AuthError(422, "INVALID_REQUEST"))

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if request.url.path.startswith("/api/auth"):
            return error_response(AuthError(403, "REQUEST_FORBIDDEN"))
        return JSONResponse({"detail": "Not found"}, status_code=exc.status_code)

    @app.middleware("http")
    async def auth_controls(request: Request, call_next):
        if not request.url.path.startswith("/api/auth"):
            return await call_next(request)
        try:
            if request.url.query or request.headers.get("authorization") is not None:
                raise AuthError(403, "REQUEST_FORBIDDEN")
            if request.method == "POST":
                if (
                    len(request.headers.getlist("origin")) != 1
                    or request.headers.get("origin") != settings.origin
                    or len(request.headers.getlist("x-csrf-token")) != 1
                ):
                    raise AuthError(403, "REQUEST_FORBIDDEN")
                if request.headers.get("content-type", "").split(";")[0] != "application/json":
                    raise AuthError(422, "INVALID_REQUEST")
                # Read a bounded stream instead of trusting Content-Length.
                payload = bytearray()
                async for chunk in request.stream():
                    payload.extend(chunk)
                    if len(payload) > 8192:
                        raise AuthError(422, "INVALID_REQUEST")
                request._body = bytes(payload)
                await run_in_threadpool(
                    app.state.identity.validate_csrf,
                    request.cookies.get(settings.session_cookie),
                    request.cookies.get(settings.csrf_cookie),
                    request.headers.get("x-csrf-token"),
                )
            response = await call_next(request)
        except AuthError as exc:
            response = error_response(exc)
        except Exception:
            # No unhandled provider/storage/input diagnostic enters logs or body.
            response = error_response(AuthError(503, "AUTH_UNAVAILABLE"))
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    return app


app = create_app()
