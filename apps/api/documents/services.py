from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from audit.services import record_audit_event

from .models import ConsentRecord, DocumentAssignment, TrainingAssignment


@transaction.atomic
def acknowledge_document(
    *,
    assignment: DocumentAssignment,
    actor_user,
    acknowledgement_text: str = "",
    evidence_label: str = "",
    request=None,
) -> DocumentAssignment:
    if assignment.status in {DocumentAssignment.Status.CANCELLED, DocumentAssignment.Status.EXPIRED}:
        raise ValidationError({"assignment": "This document assignment cannot be acknowledged."})
    assignment.status = DocumentAssignment.Status.ACKNOWLEDGED
    assignment.completed_at = timezone.now()
    assignment.acknowledgement_text = acknowledgement_text
    assignment.evidence_label = evidence_label
    assignment.save(update_fields=["status", "completed_at", "acknowledgement_text", "evidence_label", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="document.assignment.acknowledge",
        target=assignment,
        request=request,
        metadata={"template_id": assignment.template_id, "evidence_label": evidence_label},
    )
    return assignment


@transaction.atomic
def sign_document(
    *,
    assignment: DocumentAssignment,
    actor_user,
    acknowledgement_text: str = "",
    evidence_label: str = "",
    request=None,
) -> DocumentAssignment:
    if assignment.status in {DocumentAssignment.Status.CANCELLED, DocumentAssignment.Status.EXPIRED}:
        raise ValidationError({"assignment": "This document assignment cannot be signed."})
    assignment.status = DocumentAssignment.Status.SIGNED
    assignment.completed_at = timezone.now()
    assignment.acknowledgement_text = acknowledgement_text
    assignment.evidence_label = evidence_label
    assignment.save(update_fields=["status", "completed_at", "acknowledgement_text", "evidence_label", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="document.assignment.sign",
        target=assignment,
        request=request,
        metadata={"template_id": assignment.template_id, "evidence_label": evidence_label},
    )
    return assignment


@transaction.atomic
def grant_consent(
    *,
    record: ConsentRecord,
    actor_user,
    request=None,
) -> ConsentRecord:
    record.status = ConsentRecord.Status.GIVEN
    record.granted_by = actor_user
    record.granted_at = timezone.now()
    record.withdrawn_at = None
    record.save(update_fields=["status", "granted_by", "granted_at", "withdrawn_at", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="consent.grant",
        target=record,
        request=request,
        metadata={"consent_type": record.consent_type, "purpose": record.purpose},
    )
    return record


@transaction.atomic
def withdraw_consent(
    *,
    record: ConsentRecord,
    actor_user,
    request=None,
) -> ConsentRecord:
    if record.status == ConsentRecord.Status.WITHDRAWN:
        raise ValidationError({"status": "Consent is already withdrawn."})
    record.status = ConsentRecord.Status.WITHDRAWN
    record.withdrawn_at = timezone.now()
    record.save(update_fields=["status", "withdrawn_at", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="consent.withdraw",
        target=record,
        request=request,
        metadata={"consent_type": record.consent_type, "purpose": record.purpose},
    )
    return record


@transaction.atomic
def complete_training(
    *,
    assignment: TrainingAssignment,
    actor_user,
    completion_note: str = "",
    quiz_score: int | None = None,
    evidence_label: str = "",
    request=None,
) -> TrainingAssignment:
    if assignment.status in {TrainingAssignment.Status.WAIVED, TrainingAssignment.Status.EXPIRED}:
        raise ValidationError({"assignment": "This training assignment cannot be completed."})
    now = timezone.now()
    assignment.status = TrainingAssignment.Status.COMPLETED
    assignment.completed_at = now
    assignment.expires_at = now + timedelta(days=assignment.module.validity_days)
    assignment.completion_note = completion_note
    assignment.quiz_score = quiz_score
    assignment.evidence_label = evidence_label
    if assignment.module.certificate_required and not assignment.certificate_label:
        assignment.certificate_label = f"CERT-{assignment.id:06d}"
    assignment.save()
    record_audit_event(
        actor_user=actor_user,
        action="training.assignment.complete",
        target=assignment,
        request=request,
        metadata={"module_id": assignment.module_id, "quiz_score": quiz_score},
    )
    return assignment


@transaction.atomic
def review_training(
    *,
    assignment: TrainingAssignment,
    actor_user,
    status: str,
    note: str = "",
    request=None,
) -> TrainingAssignment:
    assignment.status = status
    assignment.reviewed_by = actor_user
    assignment.reviewed_at = timezone.now()
    if note:
        assignment.metadata = {**assignment.metadata, "review_note": note}
    assignment.save(update_fields=["status", "reviewed_by", "reviewed_at", "metadata", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="training.assignment.review",
        target=assignment,
        request=request,
        metadata={"module_id": assignment.module_id, "status": status, "note": note},
    )
    return assignment


def refresh_expiry_statuses(*, now=None) -> dict[str, int]:
    now = now or timezone.now()
    document_count = DocumentAssignment.objects.filter(
        status__in=[DocumentAssignment.Status.ASSIGNED, DocumentAssignment.Status.VIEWED],
        due_at__lt=now,
    ).update(status=DocumentAssignment.Status.EXPIRED)
    training_overdue_count = TrainingAssignment.objects.filter(
        status__in=[TrainingAssignment.Status.ASSIGNED, TrainingAssignment.Status.IN_PROGRESS],
        due_at__lt=now,
    ).update(status=TrainingAssignment.Status.OVERDUE)
    training_expired_count = TrainingAssignment.objects.filter(
        status=TrainingAssignment.Status.COMPLETED,
        expires_at__lt=now,
    ).update(status=TrainingAssignment.Status.EXPIRED)
    consent_count = ConsentRecord.objects.filter(
        status=ConsentRecord.Status.GIVEN,
        expires_at__lt=now,
    ).update(status=ConsentRecord.Status.EXPIRED)
    return {
        "expired_documents": document_count,
        "overdue_training": training_overdue_count,
        "expired_training": training_expired_count,
        "expired_consents": consent_count,
    }
