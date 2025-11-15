"""Version 1 API for the notification service."""

from fastapi import APIRouter

from .notifications import router as notifications_router

router = APIRouter(prefix="/v1")
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])

__all__ = ["router"]



