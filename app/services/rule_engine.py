"""Rule engine for domain-specific notification defaults."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..schemas.notification import DeliveryChannel, NotificationRequest, RoleType


@dataclass(frozen=True)
class NotificationRule:
    """Immutable rule describing default behavior for a notification event."""

    event_type: str
    default_channels: Tuple[DeliveryChannel, ...]
    target_roles: Tuple[RoleType, ...]
    description: str = ""


DEFAULT_RULES: Dict[str, NotificationRule] = {
    "credential.issued": NotificationRule(
        event_type="credential.issued",
        default_channels=(DeliveryChannel.EMAIL, DeliveryChannel.IN_APP),
        target_roles=(RoleType.LEARNER,),
        description="Learner receives notification when issuer issues a credential.",
    ),
    "credential.updated": NotificationRule(
        event_type="credential.updated",
        default_channels=(DeliveryChannel.EMAIL, DeliveryChannel.IN_APP),
        target_roles=(RoleType.LEARNER,),
        description="Learner notified when credential metadata changes.",
    ),
    "credential.revoked": NotificationRule(
        event_type="credential.revoked",
        default_channels=(DeliveryChannel.EMAIL, DeliveryChannel.IN_APP),
        target_roles=(RoleType.LEARNER,),
        description="Learner alerted when a credential is revoked.",
    ),
    "profile.viewed": NotificationRule(
        event_type="profile.viewed",
        default_channels=(DeliveryChannel.IN_APP,),
        target_roles=(RoleType.LEARNER,),
        description="Learner informed when an employer views their profile.",
    ),
    "employer.requested_verification": NotificationRule(
        event_type="employer.requested_verification",
        default_channels=(DeliveryChannel.EMAIL, DeliveryChannel.IN_APP),
        target_roles=(RoleType.ISSUER,),
        description="Issuer notified when employer requests verification.",
    ),
}


class NotificationRuleEngine:
    """Resolve notification defaults based on event metadata."""

    def __init__(self, rules: Dict[str, NotificationRule] | None = None) -> None:
        self._rules = rules or DEFAULT_RULES

    def get_rule(self, event_type: str) -> NotificationRule | None:
        """Return rule for a given event type if available."""
        return self._rules.get(event_type)

    def resolve_channels(self, request: NotificationRequest) -> List[DeliveryChannel]:
        """Determine delivery channels using request overrides or defaults."""
        if request.channels:
            return list(dict.fromkeys(request.channels))  # Preserve order, drop duplicates.

        rule = self.get_rule(request.event_type)
        if rule:
            return list(rule.default_channels)

        return [DeliveryChannel.IN_APP]

    def resolve_recipient_roles(self, request: NotificationRequest) -> List[RoleType]:
        """Determine which roles should receive the notification."""
        if request.recipient_roles:
            return list(dict.fromkeys(request.recipient_roles))

        rule = self.get_rule(request.event_type)
        if rule:
            return list(rule.target_roles)

        return []

    def describe_event(self, event_type: str) -> str | None:
        """Return human-readable description of the event."""
        rule = self.get_rule(event_type)
        return rule.description if rule else None


