"""Public directory transport. No identity cookies, input echoes, or fake data."""

from fastapi import APIRouter, Request
from fastapi.routing import APIRoute
from starlette.responses import JSONResponse, Response

from abogalia_api.marketplace.directory import DirectoryError, DirectoryQuery


class DirectoryRoute(APIRoute):
    def get_route_handler(self):
        endpoint = super().get_route_handler()

        async def handle(request):
            try:
                if "authorization" in request.headers:
                    raise DirectoryError("REQUEST_FORBIDDEN")
                async for chunk in request.stream():
                    if chunk:
                        raise DirectoryError("INVALID_REQUEST")
                request.state.directory_query = DirectoryQuery.parse(
                    request.scope.get("query_string", b""),
                    detail=bool(request.path_params),
                )
                response = await endpoint(request)
            except DirectoryError as error:
                response = JSONResponse(error.body(), status_code=error.status)
            except Exception:
                error = DirectoryError("OPERATION_UNAVAILABLE")
                response = JSONResponse(error.body(), status_code=error.status)
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
            return response

        return handle


router = APIRouter(
    prefix="/api/public/professionals", tags=["Public directory"], route_class=DirectoryRoute
)


def _service(request):
    service = getattr(request.app.state, "directory", None)
    if service is None:
        raise DirectoryError("OPERATION_UNAVAILABLE")
    return service


@router.get("")
def list_professionals(request: Request):
    return Response(
        _service(request).list(request.state.directory_query), media_type="application/json"
    )


@router.get("/{public_id}")
def professional_detail(request: Request, public_id: str):
    return Response(_service(request).detail(public_id), media_type="application/json")
