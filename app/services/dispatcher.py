"""Notification dispatcher orchestrating channel-specific delivery."""

from __future__ import annotations

import asyncio
from ..core.logging import get_logger
from ..schemas.notification import DeliveryChannel, NotificationMessage


class NotificationDispatcher:
    """Dispatch notifications to respective delivery channels."""

    def __init__(self, concurrency: int = 4) -> None:
        self._logger = get_logger(__name__)
        self._semaphore = asyncio.Semaphore(concurrency)

    async def dispatch(self, notification: NotificationMessage) -> None:
        """Dispatch notification across requested channels."""
        channels = notification.channels or [DeliveryChannel.EMAIL]
        await asyncio.gather(*(self._send(notification, channel) for channel in channels))

    async def _send(self, notification: NotificationMessage, channel: DeliveryChannel) -> None:
        """Send notification via the given channel (placeholder implementation)."""
        async with self._semaphore:
            # TODO: plug actual providers here (SES, Twilio, Firebase Cloud Messaging, etc.).
            self._logger.info(
                "Sending %s notification for event %s triggered by %s targeting roles %s to recipient(s) %s",
                channel.value,
                notification.event_type,
                notification.actor_role.value,
                [role.value for role in notification.recipient_roles],
                notification.recipients,
            )
            await asyncio.sleep(0)  # Let the event loop breathe.


