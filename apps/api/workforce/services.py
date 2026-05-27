from __future__ import annotations

from datetime import datetime, time, timedelta

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from audit.services import record_audit_event
from tickets.models import TaskCompletion

from .models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary


@transaction.atomic
def publish_shift(*, shift: Shift, actor_user, request=None) -> Shift:
    shift.status = Shift.Status.PUBLISHED
    shift.published_by = actor_user
    shift.published_at = timezone.now()
    shift.save(update_fields=["status", "published_by", "published_at", "updated_at"])
    record_audit_event(actor_user=actor_user, action="workforce.shift.publish", target=shift, request=request)
    return shift


@transaction.atomic
def review_leave_request(*, leave_request: LeaveRequest, actor_user, status: str, note: str = "", request=None):
    leave_request.status = status
    leave_request.reviewed_by = actor_user
    leave_request.reviewed_at = timezone.now()
    leave_request.review_note = note
    leave_request.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="workforce.leave.review",
        target=leave_request,
        request=request,
        metadata={"status": status, "note": note},
    )
    return leave_request


@transaction.atomic
def clock_in(*, actor_user, shift: Shift | None = None, location_label: str = "", request=None) -> AttendanceRecord:
    active = AttendanceRecord.objects.filter(
        staff_user=actor_user,
        status=AttendanceRecord.Status.CLOCKED_IN,
    ).first()
    if active:
        raise ValidationError({"attendance": "You already have an active clock-in record."})
    record = AttendanceRecord.objects.create(
        staff_user=actor_user,
        shift=shift,
        branch=shift.branch if shift else actor_user.primary_branch,
        clock_in_at=timezone.now(),
        location_label=location_label,
    )
    record_audit_event(
        actor_user=actor_user,
        action="workforce.attendance.clock_in",
        target=record,
        request=request,
        metadata={"shift_id": shift.id if shift else None},
    )
    return record


@transaction.atomic
def clock_out(*, record: AttendanceRecord, actor_user, exception_note: str = "", request=None) -> AttendanceRecord:
    if record.status != AttendanceRecord.Status.CLOCKED_IN:
        raise ValidationError({"attendance": "This attendance record is not active."})
    record.clock_out_at = timezone.now()
    record.exception_note = exception_note
    record.status = AttendanceRecord.Status.EXCEPTION if exception_note else AttendanceRecord.Status.CLOCKED_OUT
    record.save(update_fields=["clock_out_at", "exception_note", "status", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="workforce.attendance.clock_out",
        target=record,
        request=request,
        metadata={"status": record.status, "exception_note": exception_note},
    )
    return record


@transaction.atomic
def approve_attendance(*, record: AttendanceRecord, actor_user, request=None) -> AttendanceRecord:
    record.approved_by = actor_user
    record.approved_at = timezone.now()
    record.save(update_fields=["approved_by", "approved_at", "updated_at"])
    record_audit_event(actor_user=actor_user, action="workforce.attendance.approve", target=record, request=request)
    return record


@transaction.atomic
def acknowledge_handover(*, note: HandoverNote, actor_user, request=None) -> HandoverNote:
    note.status = HandoverNote.Status.ACKNOWLEDGED
    note.acknowledged_by = actor_user
    note.acknowledged_at = timezone.now()
    note.save(update_fields=["status", "acknowledged_by", "acknowledged_at", "updated_at"])
    record_audit_event(actor_user=actor_user, action="workforce.handover.acknowledge", target=note, request=request)
    return note


def minutes_between(start, end) -> int:
    if not start or not end:
        return 0
    return max(0, int((end - start).total_seconds() // 60))


@transaction.atomic
def refresh_timesheet_summary(
    *,
    staff_user,
    period_start,
    period_end,
    actor_user=None,
    request=None,
) -> TimesheetSummary:
    period_start_dt = timezone.make_aware(datetime.combine(period_start, time.min))
    period_end_dt = timezone.make_aware(datetime.combine(period_end, time.max))
    shifts = Shift.objects.filter(staff_user=staff_user, starts_at__range=(period_start_dt, period_end_dt))
    attendance = AttendanceRecord.objects.filter(
        staff_user=staff_user,
        clock_in_at__range=(period_start_dt, period_end_dt),
    )
    scheduled_minutes = sum(minutes_between(shift.starts_at, shift.ends_at) for shift in shifts)
    worked_minutes = sum(minutes_between(item.clock_in_at, item.clock_out_at) for item in attendance)
    task_minutes = (
        TaskCompletion.objects.filter(
            completed_by=staff_user,
            created_at__range=(period_start_dt, period_end_dt),
        ).aggregate(total=Sum("time_spent_minutes"))["total"]
        or 0
    )
    exception_count = attendance.filter(status=AttendanceRecord.Status.EXCEPTION).count()
    summary, _ = TimesheetSummary.objects.update_or_create(
        staff_user=staff_user,
        period_start=period_start,
        period_end=period_end,
        defaults={
            "branch": staff_user.primary_branch,
            "scheduled_minutes": scheduled_minutes,
            "worked_minutes": worked_minutes,
            "task_minutes": task_minutes,
            "exception_count": exception_count,
            "payroll_ready": worked_minutes > 0 and exception_count == 0,
        },
    )
    if actor_user:
        record_audit_event(
            actor_user=actor_user,
            action="workforce.timesheet.refresh",
            target=summary,
            request=request,
            metadata={"period_start": str(period_start), "period_end": str(period_end)},
        )
    return summary


@transaction.atomic
def submit_timesheet(*, summary: TimesheetSummary, actor_user, request=None) -> TimesheetSummary:
    summary.status = TimesheetSummary.Status.SUBMITTED
    summary.submitted_at = timezone.now()
    summary.save(update_fields=["status", "submitted_at", "updated_at"])
    record_audit_event(actor_user=actor_user, action="workforce.timesheet.submit", target=summary, request=request)
    return summary


@transaction.atomic
def review_timesheet(*, summary: TimesheetSummary, actor_user, status: str, note: str = "", request=None):
    summary.status = status
    summary.reviewed_by = actor_user
    summary.reviewed_at = timezone.now()
    summary.review_note = note
    summary.payroll_ready = status == TimesheetSummary.Status.APPROVED
    summary.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "payroll_ready", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="workforce.timesheet.review",
        target=summary,
        request=request,
        metadata={"status": status, "note": note},
    )
    return summary


def default_pay_period(now=None):
    today = (now or timezone.now()).date()
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=13)
