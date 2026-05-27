from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Shift(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="shifts")
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shifts")
    role_label = models.CharField(max_length=120, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    overtime_minutes = models.PositiveIntegerField(default=0)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_shifts",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["starts_at", "id"]
        indexes = [
            models.Index(fields=["staff_user", "starts_at"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.staff_user.email} shift {self.starts_at:%Y-%m-%d %H:%M}"


class LeaveRequest(TimeStampedModel):
    class LeaveType(models.TextChoices):
        ANNUAL = "annual", "Annual"
        SICK = "sick", "Sick"
        CARERS = "carers", "Carers"
        UNPAID = "unpaid", "Unpaid"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_requests",
    )
    leave_type = models.CharField(max_length=32, choices=LeaveType.choices, default=LeaveType.ANNUAL)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    related_ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_requests",
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["staff_user", "status"]),
            models.Index(fields=["branch", "status"]),
        ]


class AttendanceRecord(TimeStampedModel):
    class Status(models.TextChoices):
        CLOCKED_IN = "clocked_in", "Clocked In"
        CLOCKED_OUT = "clocked_out", "Clocked Out"
        EXCEPTION = "exception", "Exception"

    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    clock_in_at = models.DateTimeField()
    clock_out_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CLOCKED_IN)
    exception_note = models.TextField(blank=True)
    location_label = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_attendance_records",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-clock_in_at", "-id"]
        indexes = [
            models.Index(fields=["staff_user", "status"]),
            models.Index(fields=["branch", "clock_in_at"]),
        ]


class HandoverNote(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        CLOSED = "closed", "Closed"

    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="handover_notes")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="handover_notes",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_handover_notes",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
    due_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_handover_notes",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "due_at", "-created_at"]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["assigned_to", "status"]),
        ]


class TimesheetSummary(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        NEEDS_CORRECTION = "needs_correction", "Needs Correction"

    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="timesheet_summaries",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timesheet_summaries",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    scheduled_minutes = models.PositiveIntegerField(default=0)
    worked_minutes = models.PositiveIntegerField(default=0)
    task_minutes = models.PositiveIntegerField(default=0)
    exception_count = models.PositiveIntegerField(default=0)
    payroll_ready = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_timesheets",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-period_start", "staff_user__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["staff_user", "period_start", "period_end"],
                name="unique_timesheet_period_per_staff",
            )
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["staff_user", "period_start"]),
        ]
