from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.records import router as records_router
from app.api.v1.endpoints.upload import router as upload_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(upload_router, prefix="", tags=["upload"])
api_router.include_router(records_router, prefix="", tags=["records"])
