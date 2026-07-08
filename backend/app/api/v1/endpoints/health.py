from app.schemas.health import HealthResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
