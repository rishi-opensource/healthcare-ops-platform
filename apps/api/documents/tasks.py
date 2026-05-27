from __future__ import annotations

from celery import shared_task

from .services import refresh_expiry_statuses


@shared_task
def refresh_compliance_expiry_statuses() -> dict[str, int]:
    return refresh_expiry_statuses()
