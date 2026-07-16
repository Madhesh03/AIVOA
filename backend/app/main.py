import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings, setup_logging
from app.core.exceptions import DomainException
from app.db.session import init_db, close_db
from app.api.routers import health, hcps, interactions, assistant

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HCP CRM application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-First CRM for HCP Interactions",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"about:blank/{exc.error_code}",
                "title": exc.error_code,
                "detail": exc.message,
                "status": exc.status_code,
                "errors": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank/INTERNAL_SERVER_ERROR",
                "title": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status": 500,
            },
        )

    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(hcps.router, prefix="/api", tags=["hcps"])
    app.include_router(interactions.router, prefix="/api", tags=["interactions"])
    app.include_router(assistant.router, prefix="/api", tags=["assistant"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
