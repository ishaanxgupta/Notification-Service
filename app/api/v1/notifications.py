"""Notification endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.config import settings
from ...dependencies import get_notification_orchestrator, get_publisher
from ...messaging.publisher import NotificationPublisher
from ...schemas.notification import NotificationRequest
from ...services.orchestrator import NotificationOrchestrator


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a notification event",
)
async def enqueue_notification(
    request: NotificationRequest,
    orchestrator: NotificationOrchestrator = Depends(get_notification_orchestrator),
    publisher: NotificationPublisher = Depends(get_publisher),
) -> dict[str, str]:
    """Enqueue a notification event for async processing."""
    try:
        message = orchestrator.prepare_message(request)
        await publisher.publish(message)
        return {"status": "accepted", "event_type": message.event_type}
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue notification: {exc}",
        ) from exc


