from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Operations"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["abogalia-api"] = "abogalia-api"


@router.get("/health", response_model=HealthResponse)
async def health(response: Response) -> HealthResponse:
    """Liveness only: does not attest to database or identity readiness."""
    response.headers["Cache-Control"] = "no-store"
    return HealthResponse()
