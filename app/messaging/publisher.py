"""RabbitMQ publisher for sending notification events."""

from __future__ import annotations

import json
from typing import Optional

from aio_pika import Message

from ..core.logging import get_logger
from ..schemas.notification import NotificationMessage
from .connection import RabbitMQConnectionManager


class NotificationPublisher:
    """Publish notifications to RabbitMQ."""

    def __init__(
        self,
        connection_manager: RabbitMQConnectionManager,
        default_routing_key: str,
    ) -> None:
        self._logger = get_logger(__name__)
        self._connection_manager = connection_manager
        self._default_routing_key = default_routing_key

    async def connect(self) -> None:
        """Ensure underlying connection is ready."""
        await self._connection_manager.get_exchange()

    async def close(self) -> None:
        """Close underlying RabbitMQ resources."""
        await self._connection_manager.close()

    async def publish(
        self,
        message: NotificationMessage,
        routing_key: Optional[str] = None,
    ) -> None:
        """Publish a notification message."""
        serialized = message.model_dump_json().encode("utf-8")
        amqp_message = Message(
            body=serialized,
            content_type="application/json",
            delivery_mode=2,
            headers={
                "event_type": message.event_type,
                "source": message.source,
            },
        )
        target_routing_key = routing_key or self._default_routing_key

        await self._connection_manager.publish(amqp_message, routing_key=target_routing_key)
        self._logger.debug(
            "Notification published to %s: %s",
            target_routing_key,
            message.event_type,
        )





