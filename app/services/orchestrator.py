"""Orchestrates request enrichment before publishing notifications."""

from __future__ import annotations

from typing import List

from ..core.config import settings
from ..schemas.notification import DeliveryChannel, NotificationMessage, NotificationRequest
from .rule_engine import NotificationRuleEngine


class NotificationOrchestrator:
    """Apply domain rules to prepare enriched notification messages."""

    def __init__(self, rule_engine: NotificationRuleEngine) -> None:
        self._rule_engine = rule_engine

    def prepare_message(self, request: NotificationRequest) -> NotificationMessage:
        """Enrich the incoming request with defaults and produce a message."""
        channels = self._rule_engine.resolve_channels(request)
        recipient_roles = self._rule_engine.resolve_recipient_roles(request)

        if not recipient_roles:
            raise ValueError(
                f"No recipient roles resolved for event '{request.event_type}'. "
                "Provide recipient_roles explicitly or register a rule.",
            )

        message = request.to_message(
            source=settings.app_name,
            channels=channels,
            recipient_roles=recipient_roles,
        )

        if not message.channels:
            message.channels = [DeliveryChannel.IN_APP]

        return message


