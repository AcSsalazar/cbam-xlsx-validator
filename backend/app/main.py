from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.settings import get_settings
from fastapi import FastAPI

settings = get_settings()
configure_logging(settings.debug)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
)

register_exception_handlers(app)
app.include_router(api_router)
