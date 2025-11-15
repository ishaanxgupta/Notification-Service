"""Pydantic models for notifications."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, Field, model_validator


class DeliveryChannel(str, Enum):
    """Supported delivery channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class RoleType(str, Enum):
    """Supported domain roles."""

    ISSUER = "issuer"
    LEARNER = "learner"
    EMPLOYER = "employer"


class NotificationPayload(BaseModel):
    """Payload for a notification event."""

    subject: Optional[str] = Field(default=None, description="Subject or title of the notification.")
    body: Optional[str] = Field(default=None, description="Primary body content.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for templates.")


class NotificationMessage(BaseModel):
    """Message consumed from or published to RabbitMQ."""

    event_type: str = Field(..., description="The type of event triggering the notification.")
    source: str = Field(..., description="Identifier for the originating service.")
    actor_role: RoleType = Field(..., description="Role that generated the event.")
    recipient_roles: List[RoleType] = Field(..., description="Roles expected to receive the notification.")
    recipients: Sequence[str] = Field(..., description="Recipient identifiers (emails, phone numbers, etc.).")
    channels: Optional[List[DeliveryChannel]] = Field(default=None, description="Delivery channels to use.")
    payload: NotificationPayload = Field(default_factory=NotificationPayload, description="Notification payload.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the event.")

    @model_validator(mode="after")
    def validate_roles(self) -> "NotificationMessage":
        """Ensure the notification has at least one target role."""
        if not self.recipient_roles:
            raise ValueError("NotificationMessage requires at least one recipient role.")
        return self


class NotificationRequest(BaseModel):
    """API request to trigger a notification."""

    event_type: str
    actor_role: RoleType
    recipients: Sequence[str]
    recipient_roles: Optional[List[RoleType]] = None
    channels: Optional[List[DeliveryChannel]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_message(
        self,
        source: str,
        channels: Optional[List[DeliveryChannel]] = None,
        recipient_roles: Optional[List[RoleType]] = None,
    ) -> NotificationMessage:
        """Convert request data to a notification message."""
        resolved_channels = channels or (list(self.channels) if self.channels else None)
        resolved_roles = recipient_roles or list(self.recipient_roles or [])

        return NotificationMessage(
            event_type=self.event_type,
            source=source,
            actor_role=self.actor_role,
            recipient_roles=resolved_roles,
            recipients=list(self.recipients),
            channels=resolved_channels,
            payload=NotificationPayload(
                subject=self.subject,
                body=self.body,
                metadata=self.metadata,
            ),
        )


