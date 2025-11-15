"""RabbitMQ consumer responsible for processing notification messages."""

from __future__ import annotations

import asyncio
import json
from typing import Optional

from aio_pika import IncomingMessage

from ..core.logging import get_logger
from ..schemas.notification import NotificationMessage
from ..services.dispatcher import NotificationDispatcher
from .connection import RabbitMQConnectionManager


class NotificationConsumer:
    """Manage subscription to the notification queue and message processing."""

    def __init__(
        self,
        connection_manager: RabbitMQConnectionManager,
        dispatcher: NotificationDispatcher,
        requeue_on_error: bool = True,
    ) -> None:
        self._logger = get_logger(__name__)
        self._connection_manager = connection_manager
        self._dispatcher = dispatcher
        self._queue_consumer_tag: Optional[str] = None
        self._requeue_on_error = requeue_on_error
        self._started = asyncio.Event()
        self._queue = None

    async def start(self) -> None:
        """Begin consuming messages."""
        if self._started.is_set():
            return

        queue = await self._connection_manager.get_queue()
        self._queue = queue
        self._queue_consumer_tag = await queue.consume(self._handle_message, no_ack=False)
        self._started.set()
        self._logger.info("Notification consumer started with tag %s", self._queue_consumer_tag)

    async def stop(self) -> None:
        """Cancel queue consumption and close the connection."""
        if not self._started.is_set():
            return

        if self._queue and self._queue_consumer_tag:
            await self._queue.cancel(self._queue_consumer_tag)
            self._logger.info("Notification consumer %s stopped", self._queue_consumer_tag)

        await self._connection_manager.close()
        self._started.clear()
        self._queue_consumer_tag = None
        self._queue = None

    async def _handle_message(self, message: IncomingMessage) -> None:
        """Handle incoming RabbitMQ messages."""
        async with message.process(ignore_processed=True, requeue=self._requeue_on_error):
            try:
                payload = json.loads(message.body.decode("utf-8"))
                notification = NotificationMessage.model_validate(payload)
                await self._dispatcher.dispatch(notification)
                self._logger.debug("Notification processed: %s", notification.event_type)
            except Exception as exc:  # noqa: BLE001
                self._logger.exception("Failed to process notification: %s", exc)
                raise


