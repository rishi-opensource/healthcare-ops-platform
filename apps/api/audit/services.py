from __future__ import annotations

from typing import Any

from django.db import models

from .models import AuditEvent


def _client_ip(request) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def record_audit_event(
    *,
    actor_user=None,
    actor_entity=None,
    action: str,
    target: models.Model | None = None,
    target_type: str | None = None,
    target_id: str | int | None = None,
    branch=None,
    request=None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    if target is not None:
        target_type = target_type or target.__class__.__name__
        target_id = target_id or target.pk
        branch = branch or getattr(target, "branch", None)

    if request is not None and actor_user is None and getattr(request, "user", None):
        if request.user.is_authenticated:
            actor_user = request.user

    return AuditEvent.objects.create(
        actor_user=actor_user,
        actor_entity=actor_entity,
        action=action,
        target_type=target_type or "unknown",
        target_id=str(target_id or ""),
        branch=branch,
        request_id=(request.headers.get("X-Request-ID", "") if request is not None else ""),
        ip_address=_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request is not None else ""),
        metadata=metadata or {},
    )

