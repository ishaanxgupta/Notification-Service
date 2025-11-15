"""RabbitMQ connection manager using aio-pika."""

from __future__ import annotations

import asyncio
from typing import Literal, Optional

import aio_pika
from aio_pika import Message, RobustChannel, RobustConnection, RobustExchange, RobustQueue
from aio_pika.abc import AbstractRobustConnection

from ..core.logging import get_logger


class RabbitMQConnectionManager:
    """Manage connections, channels, exchanges, and queues for RabbitMQ."""

    def __init__(
        self,
        amqp_url: str,
        exchange: str,
        exchange_type: Literal["direct", "topic", "fanout"],
        queue: str,
        routing_key: str,
        prefetch_count: int = 64,
    ) -> None:
        self._logger = get_logger(__name__)
        self._amqp_url = amqp_url
        self._exchange_name = exchange
        self._exchange_type = exchange_type
        self._queue_name = queue
        self._routing_key = routing_key
        self._prefetch_count = prefetch_count

        self._connection: Optional[RobustConnection] = None
        self._channel: Optional[RobustChannel] = None
        self._exchange: Optional[RobustExchange] = None
        self._queue: Optional[RobustQueue] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> RobustConnection:
        """Establish a robust connection to RabbitMQ if not already connected."""
        if self._connection and not self._connection.is_closed:
            return self._connection

        self._logger.info("Connecting to RabbitMQ at %s", self._amqp_url)
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._connection.close_callbacks.add(self._on_connection_closed)
        return self._connection

    async def get_channel(self) -> RobustChannel:
        """Get or create a channel with the configured prefetch count."""
        async with self._lock:
            if self._channel and not self._channel.is_closed:
                return self._channel

            connection = await self.connect()
            self._channel = await connection.channel()
            await self._channel.set_qos(prefetch_count=self._prefetch_count)
            self._logger.info("RabbitMQ channel created with prefetch %s", self._prefetch_count)
            return self._channel

    async def get_exchange(self) -> RobustExchange:
        """Return a declared exchange."""
        if self._exchange:
            return self._exchange

        channel = await self.get_channel()
        self._exchange = await channel.declare_exchange(
            self._exchange_name,
            type=self._exchange_type,
            durable=True,
        )
        self._logger.info("Exchange %s declared", self._exchange_name)
        return self._exchange

    async def get_queue(self) -> RobustQueue:
        """Return a declared queue bound to the default exchange."""
        if self._queue:
            return self._queue

        channel = await self.get_channel()
        self._queue = await channel.declare_queue(self._queue_name, durable=True)
        await self._queue.bind(await self.get_exchange(), routing_key=self._routing_key)
        self._logger.info(
            "Queue %s declared and bound to exchange %s with routing key %s",
            self._queue_name,
            self._exchange_name,
            self._routing_key,
        )
        return self._queue

    async def publish(self, message: Message, routing_key: Optional[str] = None) -> None:
        """Publish a message to the exchange."""
        exchange = await self.get_exchange()
        await exchange.publish(message, routing_key=routing_key or self._routing_key)

    async def close(self) -> None:
        """Close all RabbitMQ resources gracefully."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            self._logger.debug("Channel closed")
            self._channel = None

        self._queue = None

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            self._logger.info("RabbitMQ connection closed")
            self._connection = None

    def _on_connection_closed(self, _: AbstractRobustConnection, exc: BaseException | None) -> None:
        """Handle unexpected connection closures."""
        if exc:
            self._logger.error("RabbitMQ connection closed unexpectedly: %s", exc)
        else:
            self._logger.info("RabbitMQ connection closed gracefully.")


