from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from audit.services import record_audit_event

from .models import TaskCompletion, Ticket, TicketApproval, TicketComment, TicketStatusHistory

ALLOWED_TRANSITIONS = {
    Ticket.Status.DRAFT: {Ticket.Status.OPEN, Ticket.Status.CANCELLED},
    Ticket.Status.OPEN: {
        Ticket.Status.IN_PROGRESS,
        Ticket.Status.WAITING_APPROVAL,
        Ticket.Status.COMPLETED,
        Ticket.Status.CANCELLED,
    },
    Ticket.Status.IN_PROGRESS: {
        Ticket.Status.WAITING_APPROVAL,
        Ticket.Status.NEEDS_CORRECTION,
        Ticket.Status.COMPLETED,
        Ticket.Status.CANCELLED,
    },
    Ticket.Status.WAITING_APPROVAL: {
        Ticket.Status.NEEDS_CORRECTION,
        Ticket.Status.COMPLETED,
        Ticket.Status.CANCELLED,
    },
    Ticket.Status.NEEDS_CORRECTION: {
        Ticket.Status.IN_PROGRESS,
        Ticket.Status.WAITING_APPROVAL,
        Ticket.Status.CANCELLED,
    },
    Ticket.Status.COMPLETED: {Ticket.Status.CLOSED},
    Ticket.Status.CLOSED: set(),
    Ticket.Status.CANCELLED: set(),
}


def next_ticket_number(ticket_id: int) -> str:
    return f"HD-{ticket_id:06d}"


@transaction.atomic
def create_ticket(*, actor_user, request=None, **fields) -> Ticket:
    ticket = Ticket.objects.create(created_by=actor_user, **fields)
    if not ticket.ticket_number:
        ticket.ticket_number = next_ticket_number(ticket.id)
        ticket.save(update_fields=["ticket_number"])
    TicketStatusHistory.objects.create(
        ticket=ticket,
        from_status="",
        to_status=ticket.status,
        changed_by=actor_user,
        note="Ticket created",
    )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.create",
        target=ticket,
        request=request,
        metadata={"ticket_number": ticket.ticket_number},
    )
    return ticket


@transaction.atomic
def transition_ticket(*, ticket: Ticket, actor_user, to_status: str, note: str = "", request=None) -> Ticket:
    from_status = ticket.status
    if from_status == to_status:
        raise ValidationError({"status": "Ticket is already in this status."})
    if to_status not in ALLOWED_TRANSITIONS.get(from_status, set()):
        raise ValidationError({"status": f"Cannot transition from {from_status} to {to_status}."})
    ticket.status = to_status
    update_fields = ["status", "updated_at"]
    if to_status == Ticket.Status.COMPLETED:
        ticket.completed_at = timezone.now()
        update_fields.append("completed_at")
    ticket.save(update_fields=update_fields)
    TicketStatusHistory.objects.create(
        ticket=ticket,
        from_status=from_status,
        to_status=to_status,
        changed_by=actor_user,
        note=note,
    )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.transition",
        target=ticket,
        request=request,
        metadata={"from_status": from_status, "to_status": to_status, "note": note},
    )
    return ticket


@transaction.atomic
def assign_ticket(*, ticket: Ticket, actor_user, assigned_to, note: str = "", request=None) -> Ticket:
    previous_assignee = ticket.assigned_to
    ticket.assigned_to = assigned_to
    ticket.save(update_fields=["assigned_to", "updated_at"])
    TicketComment.objects.create(
        ticket=ticket,
        author=actor_user,
        body=note or f"Assigned to {assigned_to.email if assigned_to else 'unassigned'}.",
        is_internal=True,
    )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.assign",
        target=ticket,
        request=request,
        metadata={
            "from_user_id": previous_assignee.id if previous_assignee else None,
            "to_user_id": assigned_to.id if assigned_to else None,
            "note": note,
        },
    )
    return ticket


@transaction.atomic
def add_ticket_comment(
    *,
    ticket: Ticket,
    actor_user,
    body: str,
    is_internal: bool = True,
    request=None,
) -> TicketComment:
    comment = TicketComment.objects.create(
        ticket=ticket,
        author=actor_user,
        body=body,
        is_internal=is_internal,
    )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.comment",
        target=ticket,
        request=request,
        metadata={"comment_id": comment.id, "is_internal": is_internal},
    )
    return comment


@transaction.atomic
def complete_ticket(
    *,
    ticket: Ticket,
    actor_user,
    completion_summary: str,
    task_name: str = "",
    task_category: str = "",
    time_spent_minutes: int = 0,
    outcome: str = "",
    request_approval: bool = True,
    request=None,
) -> Ticket:
    ticket.completion_summary = completion_summary
    ticket.completed_at = timezone.now()
    next_status = Ticket.Status.WAITING_APPROVAL if request_approval else Ticket.Status.COMPLETED
    from_status = ticket.status
    ticket.status = next_status
    ticket.save(update_fields=["completion_summary", "completed_at", "status", "updated_at"])
    TaskCompletion.objects.update_or_create(
        ticket=ticket,
        defaults={
            "completed_by": actor_user,
            "task_name": task_name or ticket.title,
            "task_category": task_category or ticket.category,
            "time_spent_minutes": time_spent_minutes,
            "outcome": outcome or completion_summary,
        },
    )
    TicketStatusHistory.objects.create(
        ticket=ticket,
        from_status=from_status,
        to_status=next_status,
        changed_by=actor_user,
        note=completion_summary,
    )
    if request_approval:
        TicketApproval.objects.create(ticket=ticket, requested_by=actor_user)
    record_audit_event(
        actor_user=actor_user,
        action="ticket.complete",
        target=ticket,
        request=request,
        metadata={
            "from_status": from_status,
            "to_status": next_status,
            "request_approval": request_approval,
            "time_spent_minutes": time_spent_minutes,
        },
    )
    return ticket


@transaction.atomic
def request_ticket_approval(
    *,
    ticket: Ticket,
    actor_user,
    approval_type: str = "ticket_completion",
    note: str = "",
    request=None,
) -> TicketApproval:
    approval = TicketApproval.objects.create(
        ticket=ticket,
        approval_type=approval_type,
        requested_by=actor_user,
    )
    if ticket.status != Ticket.Status.WAITING_APPROVAL:
        transition_ticket(
            ticket=ticket,
            actor_user=actor_user,
            to_status=Ticket.Status.WAITING_APPROVAL,
            note=note or f"Requested {approval_type} approval.",
            request=request,
        )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.approval.request",
        target=ticket,
        request=request,
        metadata={"approval_id": approval.id, "approval_type": approval_type, "note": note},
    )
    return approval


@transaction.atomic
def review_ticket_approval(
    *,
    approval: TicketApproval,
    actor_user,
    status: str,
    decision_note: str = "",
    request=None,
) -> TicketApproval:
    if approval.status != TicketApproval.Status.PENDING:
        raise ValidationError({"approval": "This approval has already been reviewed."})
    approval.status = status
    approval.reviewed_by = actor_user
    approval.reviewed_at = timezone.now()
    approval.decision_note = decision_note
    approval.save(update_fields=["status", "reviewed_by", "reviewed_at", "decision_note", "updated_at"])
    if status == TicketApproval.Status.APPROVED and approval.ticket.status == Ticket.Status.WAITING_APPROVAL:
        transition_ticket(
            ticket=approval.ticket,
            actor_user=actor_user,
            to_status=Ticket.Status.COMPLETED,
            note=decision_note or "Approval granted.",
            request=request,
        )
    elif (
        status == TicketApproval.Status.CORRECTION_REQUESTED
        and approval.ticket.status == Ticket.Status.WAITING_APPROVAL
    ):
        transition_ticket(
            ticket=approval.ticket,
            actor_user=actor_user,
            to_status=Ticket.Status.NEEDS_CORRECTION,
            note=decision_note or "Correction requested.",
            request=request,
        )
    record_audit_event(
        actor_user=actor_user,
        action="ticket.approval.review",
        target=approval.ticket,
        request=request,
        metadata={"approval_id": approval.id, "status": status, "decision_note": decision_note},
    )
    return approval
