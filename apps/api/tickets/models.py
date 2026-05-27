from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Ticket(TimeStampedModel):
    class Category(models.TextChoices):
        GENERAL = "general", "General"
        ONBOARDING = "onboarding", "Onboarding"
        PATIENT = "patient", "Patient"
        APPOINTMENT = "appointment", "Appointment"
        INVENTORY = "inventory", "Inventory"
        PURCHASE_ORDER = "purchase_order", "Purchase Order"
        PAYROLL = "payroll", "Payroll"
        LEAVE = "leave", "Leave"
        INCIDENT = "incident", "Incident"
        CONTRACT = "contract", "Contract"
        AI_CREATED = "ai_created", "AI Created"
        SUPPLIER = "supplier", "Supplier"
        MAINTENANCE = "maintenance", "Maintenance"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_APPROVAL = "waiting_approval", "Waiting Approval"
        NEEDS_CORRECTION = "needs_correction", "Needs Correction"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Source(models.TextChoices):
        WEB = "web", "Web"
        MOBILE = "mobile", "Mobile"
        ADMIN = "admin", "Admin"
        AI = "ai", "AI"
        SYSTEM = "system", "System"

    ticket_number = models.CharField(max_length=32, unique=True, blank=True)
    category = models.CharField(max_length=64, choices=Category.choices, default=Category.GENERAL)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=32, choices=Priority.choices, default=Priority.NORMAL)
    due_at = models.DateTimeField(null=True, blank=True)
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tickets",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    related_entity = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.WEB)
    completion_summary = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.ticket_number or 'TBD'} - {self.title}"


class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=32, blank=True)
    to_status = models.CharField(max_length=32)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_status_changes",
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class TicketComment(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_comments",
    )
    body = models.TextField()
    is_internal = models.BooleanField(default=True)


class TicketAttachment(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_attachments",
    )
    file = models.FileField(upload_to="ticket-attachments/")
    label = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)


class TicketApproval(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CORRECTION_REQUESTED = "correction_requested", "Correction Requested"

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="approvals")
    approval_type = models.CharField(max_length=80, default="ticket_completion")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_ticket_approvals",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_ticket_approvals",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)


class TaskCompletion(TimeStampedModel):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="task_completion")
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_completions",
    )
    task_name = models.CharField(max_length=255)
    task_category = models.CharField(max_length=80, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    outcome = models.TextField(blank=True)
    payroll_link_approved = models.BooleanField(default=False)
    appraisal_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    appraisal_comments = models.TextField(blank=True)


class TicketLink(TimeStampedModel):
    from_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="outgoing_links")
    to_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="incoming_links")
    relationship = models.CharField(max_length=80, default="related")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_ticket", "to_ticket", "relationship"],
                name="unique_ticket_link_relationship",
            )
        ]

