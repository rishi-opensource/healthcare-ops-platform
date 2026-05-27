from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class DocumentTemplate(TimeStampedModel):
    class TemplateType(models.TextChoices):
        EMPLOYMENT_AGREEMENT = "employment_agreement", "Employment Agreement"
        CONTRACTOR_AGREEMENT = "contractor_agreement", "Contractor Agreement"
        PRACTITIONER_AGREEMENT = "practitioner_agreement", "Practitioner Agreement"
        SUPPLIER_AGREEMENT = "supplier_agreement", "Supplier Agreement"
        CONFIDENTIALITY = "confidentiality", "Confidentiality Agreement"
        PRIVACY_ACKNOWLEDGEMENT = "privacy_acknowledgement", "Privacy Acknowledgement"
        AI_USAGE = "ai_usage", "AI Usage Acknowledgement"
        PATIENT_CONSENT = "patient_consent", "Patient Consent"
        POLICY = "policy", "Policy Acknowledgement"

    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=80, choices=TemplateType.choices)
    description = models.TextField(blank=True)
    current_version = models.CharField(max_length=40, default="1.0")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class DocumentFile(TimeStampedModel):
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    file = models.FileField(upload_to="documents/")
    version = models.CharField(max_length=40, default="1.0")
    label = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)


class DocumentAssignment(TimeStampedModel):
    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        VIEWED = "viewed", "Viewed"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        SIGNED = "signed", "Signed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, related_name="assignments")
    assigned_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_assignments",
    )
    assigned_to_entity = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_document_assignments",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ASSIGNED)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    signed_file = models.ForeignKey(
        DocumentFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_assignments",
    )
    version = models.CharField(max_length=40, default="1.0")
    acknowledgement_text = models.TextField(blank=True)
    evidence_label = models.CharField(max_length=255, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    renewal_ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_renewals",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["assigned_to_user", "status"]),
            models.Index(fields=["assigned_to_entity", "status"]),
        ]


class ConsentRecord(TimeStampedModel):
    class ConsentType(models.TextChoices):
        PRIVACY = "privacy", "Privacy"
        AI_USAGE = "ai_usage", "AI Usage"
        PATIENT_COMMUNICATION = "patient_communication", "Patient Communication"
        TELEHEALTH = "telehealth", "Telehealth"
        GENERAL = "general", "General"

    class Status(models.TextChoices):
        GIVEN = "given", "Given"
        WITHDRAWN = "withdrawn", "Withdrawn"
        EXPIRED = "expired", "Expired"

    consent_type = models.CharField(max_length=80, choices=ConsentType.choices)
    subject_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consent_records",
    )
    subject_entity = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consent_records",
    )
    document_assignment = models.ForeignKey(
        DocumentAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consent_records",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.GIVEN)
    purpose = models.CharField(max_length=255)
    scope = models.TextField(blank=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_consent_records",
    )
    granted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["consent_type", "status"]),
            models.Index(fields=["subject_user", "status"]),
            models.Index(fields=["subject_entity", "status"]),
        ]


class TrainingModule(TimeStampedModel):
    class ModuleType(models.TextChoices):
        PRIVACY = "privacy", "Privacy"
        CYBER_SECURITY = "cyber_security", "Cyber Security"
        EMERGENCY = "emergency", "Emergency"
        AI_GOVERNANCE = "ai_governance", "AI Governance"
        INFECTION_CONTROL = "infection_control", "Infection Control"
        BARCODE_INVENTORY = "barcode_inventory", "Barcode and Inventory"
        POLICY = "policy", "Policy"
        GENERAL = "general", "General"

    title = models.CharField(max_length=255)
    module_type = models.CharField(max_length=80, choices=ModuleType.choices, default=ModuleType.GENERAL)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=40, default="1.0")
    validity_days = models.PositiveIntegerField(default=365)
    quiz_required = models.BooleanField(default=False)
    certificate_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class TrainingAssignment(TimeStampedModel):
    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"
        EXPIRED = "expired", "Expired"
        WAIVED = "waived", "Waived"

    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name="assignments")
    assigned_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_assignments",
    )
    assigned_to_entity = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_training_assignments",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ASSIGNED)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_training_assignments",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    completion_note = models.TextField(blank=True)
    quiz_score = models.PositiveSmallIntegerField(null=True, blank=True)
    certificate_label = models.CharField(max_length=255, blank=True)
    evidence_label = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["status", "due_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["assigned_to_user", "status"]),
            models.Index(fields=["assigned_to_entity", "status"]),
        ]
