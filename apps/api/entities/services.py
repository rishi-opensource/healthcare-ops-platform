from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from audit.services import record_audit_event
from documents.models import DocumentAssignment
from tickets.models import Ticket
from tickets.services import create_ticket

from .models import (
    AIAgentProfile,
    AssetProfile,
    Entity,
    EntityLifecycleEvent,
    EntityOnboarding,
    InventoryItemProfile,
    OnboardingStepCompletion,
    OnboardingWorkflowTemplate,
    PatientReferenceProfile,
    StaffProfile,
    SupplierProfile,
)

PROFILE_MODEL_BY_ENTITY_TYPE = {
    Entity.Types.EMPLOYEE: StaffProfile,
    Entity.Types.DOCTOR: StaffProfile,
    Entity.Types.CONTRACTOR: StaffProfile,
    Entity.Types.SUPPLIER: SupplierProfile,
    Entity.Types.PATIENT_REFERENCE: PatientReferenceProfile,
    Entity.Types.INVENTORY_ITEM: InventoryItemProfile,
    Entity.Types.MEDICINE: InventoryItemProfile,
    Entity.Types.EQUIPMENT: AssetProfile,
    Entity.Types.DEVICE: AssetProfile,
    Entity.Types.ROOM: AssetProfile,
    Entity.Types.AI_AGENT: AIAgentProfile,
}

PROFILE_FIELDS = {
    StaffProfile: {"user", "employment_type", "onboarding_status", "payroll_status"},
    SupplierProfile: {"supplier_code", "payment_status", "compliance_status"},
    PatientReferenceProfile: {
        "patient_reference",
        "preferred_contact_channel",
        "masked_contact",
        "consent_status",
    },
    AssetProfile: {"asset_tag", "serial_number", "maintenance_status"},
    InventoryItemProfile: {"sku", "barcode", "unit", "reorder_threshold"},
    AIAgentProfile: {"agent_code", "human_review_required", "allowed_actions"},
}


def qr_code_for(entity: Entity) -> str:
    return f"HD-ENTITY-{entity.id:06d}"


def _profile_payload(profile_model, profile: dict) -> dict:
    allowed = PROFILE_FIELDS.get(profile_model, set())
    payload = {key: value for key, value in profile.items() if key in allowed}
    if profile_model is StaffProfile and "user" in payload and isinstance(payload["user"], int):
        payload["user_id"] = payload.pop("user")
    return payload


@transaction.atomic
def create_entity_with_profile(*, actor_user, request=None, profile: dict | None = None, **fields) -> Entity:
    entity = Entity.objects.create(**fields)
    if not entity.qr_code_value:
        entity.qr_code_value = qr_code_for(entity)
        entity.save(update_fields=["qr_code_value"])
    profile_model = PROFILE_MODEL_BY_ENTITY_TYPE.get(entity.entity_type)
    if profile_model:
        payload = _profile_payload(profile_model, profile or {})
        if profile_model is PatientReferenceProfile and not payload.get("patient_reference"):
            payload["patient_reference"] = entity.external_reference or f"PAT-{entity.id:06d}"
        if profile_model is AIAgentProfile and not payload.get("agent_code"):
            payload["agent_code"] = entity.external_reference or f"AI-{entity.id:06d}"
        profile_model.objects.create(entity=entity, **payload)
    EntityLifecycleEvent.objects.create(
        entity=entity,
        from_status="",
        to_status=entity.status,
        changed_by=actor_user,
        note="Entity created",
    )
    record_audit_event(
        actor_user=actor_user,
        action="entity.create",
        target=entity,
        request=request,
        metadata={"entity_type": entity.entity_type, "qr_code_value": entity.qr_code_value},
    )
    return entity


@transaction.atomic
def transition_entity_status(*, entity: Entity, actor_user, status: str, note: str = "", request=None) -> Entity:
    if entity.status == status:
        raise ValidationError({"status": "Entity is already in this status."})
    previous = entity.status
    entity.status = status
    entity.save(update_fields=["status", "updated_at"])
    EntityLifecycleEvent.objects.create(
        entity=entity,
        from_status=previous,
        to_status=status,
        changed_by=actor_user,
        note=note,
    )
    record_audit_event(
        actor_user=actor_user,
        action="entity.status.transition",
        target=entity,
        request=request,
        metadata={"from_status": previous, "to_status": status, "note": note},
    )
    return entity


def matching_workflow_template(entity: Entity, workflow_template_id: int | None = None):
    queryset = OnboardingWorkflowTemplate.objects.filter(is_active=True, entity_type=entity.entity_type)
    if workflow_template_id:
        return queryset.get(id=workflow_template_id)
    return queryset.order_by("id").first()


@transaction.atomic
def start_entity_onboarding(
    *,
    entity: Entity,
    actor_user,
    workflow_template_id: int | None = None,
    create_activation_ticket: bool = True,
    note: str = "",
    request=None,
) -> EntityOnboarding:
    workflow_template = matching_workflow_template(entity, workflow_template_id)
    if not workflow_template:
        raise ValidationError(
            {"workflow_template": "No active onboarding workflow template exists for this entity type."}
        )
    onboarding, created = EntityOnboarding.objects.get_or_create(
        entity=entity,
        defaults={
            "workflow_template": workflow_template,
            "status": EntityOnboarding.Status.IN_PROGRESS,
            "started_by": actor_user,
            "started_at": timezone.now(),
        },
    )
    if not created and onboarding.status in {EntityOnboarding.Status.COMPLETED, EntityOnboarding.Status.CANCELLED}:
        raise ValidationError({"onboarding": "This onboarding workflow cannot be restarted."})
    onboarding.workflow_template = workflow_template
    onboarding.status = EntityOnboarding.Status.IN_PROGRESS
    onboarding.started_by = onboarding.started_by or actor_user
    onboarding.started_at = onboarding.started_at or timezone.now()
    onboarding.save(update_fields=["workflow_template", "status", "started_by", "started_at", "updated_at"])

    if entity.status != Entity.Status.ONBOARDING:
        transition_entity_status(
            entity=entity,
            actor_user=actor_user,
            status=Entity.Status.ONBOARDING,
            note=note or "Onboarding started.",
            request=request,
        )

    for step in workflow_template.steps.select_related("document_template").all():
        completion, _ = OnboardingStepCompletion.objects.get_or_create(
            onboarding=onboarding,
            step_template=step,
            defaults={
                "name": step.name,
                "step_type": step.step_type,
                "metadata": step.metadata,
            },
        )
        if step.document_template and not completion.document_assignment:
            assignment = DocumentAssignment.objects.create(
                template=step.document_template,
                assigned_to_user=entity.owner_user,
                assigned_to_entity=entity,
                assigned_by=actor_user,
            )
            completion.document_assignment = assignment
            completion.save(update_fields=["document_assignment", "updated_at"])
        if step.ticket_category and not completion.related_ticket:
            ticket = create_ticket(
                actor_user=actor_user,
                title=f"{entity.display_name}: {step.name}",
                description=f"Complete onboarding step for {entity.display_name}.",
                category=step.ticket_category,
                priority=Ticket.Priority.NORMAL,
                branch=entity.branch,
                assigned_to=entity.responsible_user,
                related_entity=entity,
                source=Ticket.Source.SYSTEM,
                request=request,
            )
            completion.related_ticket = ticket
            completion.save(update_fields=["related_ticket", "updated_at"])

    if create_activation_ticket and not onboarding.activation_ticket:
        onboarding.activation_ticket = create_ticket(
            actor_user=actor_user,
            title=f"Activate entity: {entity.display_name}",
            description="Review completed onboarding steps and activate the entity.",
            category=Ticket.Category.ONBOARDING,
            priority=Ticket.Priority.NORMAL,
            branch=entity.branch,
            assigned_to=entity.responsible_user,
            related_entity=entity,
            source=Ticket.Source.SYSTEM,
            request=request,
        )
        onboarding.save(update_fields=["activation_ticket", "updated_at"])

    record_audit_event(
        actor_user=actor_user,
        action="entity.onboarding.start",
        target=entity,
        request=request,
        metadata={"workflow_template_id": workflow_template.id},
    )
    return onboarding


@transaction.atomic
def complete_onboarding_step(
    *,
    step_completion: OnboardingStepCompletion,
    actor_user,
    status: str,
    note: str = "",
    evidence_label: str = "",
    request=None,
) -> OnboardingStepCompletion:
    step_completion.status = status
    step_completion.note = note
    step_completion.evidence_label = evidence_label
    if status in {
        OnboardingStepCompletion.Status.COMPLETED,
        OnboardingStepCompletion.Status.VERIFIED,
        OnboardingStepCompletion.Status.WAIVED,
    }:
        step_completion.completed_by = actor_user
        step_completion.completed_at = timezone.now()
    if status == OnboardingStepCompletion.Status.VERIFIED:
        step_completion.verified_by = actor_user
        step_completion.verified_at = timezone.now()
    step_completion.save()
    refresh_onboarding_status(step_completion.onboarding, actor_user=actor_user, request=request)
    record_audit_event(
        actor_user=actor_user,
        action="entity.onboarding.step.update",
        target=step_completion.onboarding.entity,
        request=request,
        metadata={"step_completion_id": step_completion.id, "status": status},
    )
    return step_completion


def refresh_onboarding_status(onboarding: EntityOnboarding, *, actor_user=None, request=None) -> EntityOnboarding:
    required_steps = onboarding.step_completions.exclude(
        status__in=[OnboardingStepCompletion.Status.WAIVED]
    )
    total = required_steps.count()
    complete = required_steps.filter(
        status__in=[OnboardingStepCompletion.Status.COMPLETED, OnboardingStepCompletion.Status.VERIFIED]
    ).count()
    if total and total == complete:
        onboarding.status = EntityOnboarding.Status.WAITING_APPROVAL
        onboarding.save(update_fields=["status", "updated_at"])
        record_audit_event(
            actor_user=actor_user,
            action="entity.onboarding.waiting_approval",
            target=onboarding.entity,
            request=request,
            metadata={"completed_steps": complete, "required_steps": total},
        )
    return onboarding


@transaction.atomic
def activate_onboarded_entity(*, entity: Entity, actor_user, note: str = "", request=None) -> Entity:
    onboarding = getattr(entity, "onboarding", None)
    if not onboarding:
        raise ValidationError({"onboarding": "Entity onboarding has not been started."})
    pending_required = onboarding.step_completions.exclude(
        status__in=[
            OnboardingStepCompletion.Status.COMPLETED,
            OnboardingStepCompletion.Status.VERIFIED,
            OnboardingStepCompletion.Status.WAIVED,
        ]
    ).exists()
    if pending_required:
        raise ValidationError({"onboarding": "Required onboarding steps are still pending."})
    onboarding.status = EntityOnboarding.Status.COMPLETED
    onboarding.completed_by = actor_user
    onboarding.completed_at = timezone.now()
    onboarding.save(update_fields=["status", "completed_by", "completed_at", "updated_at"])
    return transition_entity_status(
        entity=entity,
        actor_user=actor_user,
        status=Entity.Status.ACTIVE,
        note=note or "Onboarding completed and entity activated.",
        request=request,
    )
