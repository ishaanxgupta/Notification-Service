"""Configuration module for the notification service."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="CredApp Notification Service", description="Human readable service name.")
    app_version: str = Field(default="0.1.0", description="Version of the notification service.")

    rabbitmq_url: AnyUrl = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="Connection URL for RabbitMQ.",
    )
    rabbitmq_exchange: str = Field(default="notifications.exchange", description="Exchange used for notifications.")
    rabbitmq_exchange_type: Literal["direct", "topic", "fanout"] = Field(
        default="topic",
        description="Type of exchange to use.",
    )
    rabbitmq_queue: str = Field(default="notifications.queue", description="Durable queue name.")
    rabbitmq_routing_key: str = Field(default="notifications.*", description="Routing key pattern for subscriptions.")
    rabbitmq_publish_routing_key: str = Field(
        default="notifications.broadcast",
        description="Default routing key used when publishing outgoing notifications.",
    )
    rabbitmq_prefetch_count: int = Field(default=64, description="Prefetch count per consumer for RabbitMQ.")
    rabbitmq_requeue_on_error: bool = Field(default=True, description="Whether to requeue failed messages.")

    worker_concurrency: int = Field(default=4, description="Number of concurrent notification tasks per instance.")
    worker_batch_size: int = Field(default=1, description="Number of messages to process per batch.")

    log_level: str = Field(default="INFO", description="Service log level.")
    tracing_enabled: bool = Field(default=False, description="Enable OpenTelemetry tracing.")
    metrics_enabled: bool = Field(default=True, description="Expose Prometheus metrics.")
    metrics_host: str = Field(default="0.0.0.0", description="Interface for metrics endpoint.")
    metrics_port: int = Field(default=9000, description="Port for metrics endpoint.")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()




