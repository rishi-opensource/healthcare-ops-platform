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

    class Meta:
        indexes = [
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["assigned_to_user", "status"]),
            models.Index(fields=["assigned_to_entity", "status"]),
        ]

