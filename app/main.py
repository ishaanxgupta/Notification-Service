"""Application entry point for the notification microservice."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import settings
from .core.logging import configure_logging
from .dependencies import get_notification_consumer, get_publisher
from .api.v1 import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context to manage startup and shutdown events."""
    configure_logging(settings.log_level)
    consumer = await get_notification_consumer()
    publisher = await get_publisher()

    await consumer.start()
    await publisher.connect()

    try:
        yield
    finally:
        await asyncio.gather(
            consumer.stop(),
            publisher.close(),
        )


def create_app() -> FastAPI:
    """Factory to create the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


