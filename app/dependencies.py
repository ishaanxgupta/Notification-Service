"""FastAPI dependencies and shared singletons."""

from __future__ import annotations

from functools import lru_cache

from .core.config import settings
from .messaging.connection import RabbitMQConnectionManager
from .messaging.consumer import NotificationConsumer
from .messaging.publisher import NotificationPublisher
from .services.dispatcher import NotificationDispatcher
from .services.orchestrator import NotificationOrchestrator
from .services.rule_engine import NotificationRuleEngine


@lru_cache
def get_connection_manager() -> RabbitMQConnectionManager:
    """Return a cached RabbitMQ connection manager instance."""
    return RabbitMQConnectionManager(
        amqp_url=str(settings.rabbitmq_url),
        exchange=settings.rabbitmq_exchange,
        exchange_type=settings.rabbitmq_exchange_type,
        queue=settings.rabbitmq_queue,
        routing_key=settings.rabbitmq_routing_key,
        prefetch_count=settings.rabbitmq_prefetch_count,
    )


@lru_cache
def get_notification_dispatcher() -> NotificationDispatcher:
    """Return a cached notification dispatcher."""
    return NotificationDispatcher(concurrency=settings.worker_concurrency)


@lru_cache
def get_rule_engine() -> NotificationRuleEngine:
    """Return the notification rule engine."""
    return NotificationRuleEngine()


@lru_cache
def get_notification_orchestrator() -> NotificationOrchestrator:
    """Return a notification orchestrator instance."""
    return NotificationOrchestrator(rule_engine=get_rule_engine())


async def get_notification_consumer() -> NotificationConsumer:
    """Return an initialized notification consumer."""
    manager = get_connection_manager()
    dispatcher = get_notification_dispatcher()
    consumer = NotificationConsumer(
        connection_manager=manager,
        dispatcher=dispatcher,
        requeue_on_error=settings.rabbitmq_requeue_on_error,
    )
    return consumer


async def get_publisher() -> NotificationPublisher:
    """Return a notification publisher bound to RabbitMQ."""
    manager = get_connection_manager()
    publisher = NotificationPublisher(
        connection_manager=manager,
        default_routing_key=settings.rabbitmq_publish_routing_key,
    )
    return publisher


