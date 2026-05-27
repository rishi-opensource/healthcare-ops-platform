from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Entity(TimeStampedModel):
    class Types(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        DOCTOR = "doctor", "Doctor / Practitioner"
        CONTRACTOR = "contractor", "Contractor"
        SUPPLIER = "supplier", "Supplier"
        PATIENT_REFERENCE = "patient_reference", "Patient Reference"
        AI_AGENT = "ai_agent", "AI Agent"
        INVENTORY_ITEM = "inventory_item", "Inventory Item"
        MEDICINE = "medicine", "Medicine"
        EQUIPMENT = "equipment", "Equipment"
        DEVICE = "device", "Device"
        ROOM = "room", "Room"
        BRANCH = "branch", "Branch"
        CONTRACT = "contract", "Contract"
        SERVICE = "service", "Service"
        DIGITAL_ASSET = "digital_asset", "Digital Asset"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ONBOARDING = "onboarding", "Onboarding"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    entity_type = models.CharField(max_length=64, choices=Types.choices)
    display_name = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entities",
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_entities",
    )
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_entities",
    )
    external_reference = models.CharField(max_length=120, blank=True)
    qr_code_value = models.CharField(max_length=255, blank=True, unique=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_name"]
        indexes = [
            models.Index(fields=["entity_type", "status"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class EntityLifecycleEvent(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="lifecycle_events")
    from_status = models.CharField(max_length=32, blank=True)
    to_status = models.CharField(max_length=32)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entity_lifecycle_changes",
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class OnboardingWorkflowTemplate(TimeStampedModel):
    entity_type = models.CharField(max_length=64, choices=Entity.Types.choices)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["entity_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["entity_type", "name"],
                name="unique_onboarding_template_name_per_type",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_entity_type_display()} - {self.name}"


class OnboardingStepTemplate(TimeStampedModel):
    class StepType(models.TextChoices):
        PROFILE = "profile", "Profile"
        DOCUMENT = "document", "Document"
        APPROVAL = "approval", "Approval"
        TRAINING = "training", "Training"
        EQUIPMENT = "equipment", "Equipment"
        QR_BARCODE = "qr_barcode", "QR / Barcode"
        REVIEW = "review", "Review"

    workflow_template = models.ForeignKey(
        OnboardingWorkflowTemplate,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    name = models.CharField(max_length=255)
    step_type = models.CharField(max_length=40, choices=StepType.choices)
    order = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    document_template = models.ForeignKey(
        "documents.DocumentTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_step_templates",
    )
    ticket_category = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["workflow_template", "order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["workflow_template", "order"],
                name="unique_onboarding_step_order_per_template",
            )
        ]

    def __str__(self) -> str:
        return self.name


class EntityOnboarding(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_APPROVAL = "waiting_approval", "Waiting Approval"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="onboarding")
    workflow_template = models.ForeignKey(
        OnboardingWorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_runs",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOT_STARTED)
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="started_entity_onboardings",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_entity_onboardings",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    activation_ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entity_onboardings",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "started_at"]),
        ]


class OnboardingStepCompletion(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        VERIFIED = "verified", "Verified"
        NEEDS_CORRECTION = "needs_correction", "Needs Correction"
        WAIVED = "waived", "Waived"

    onboarding = models.ForeignKey(EntityOnboarding, on_delete=models.CASCADE, related_name="step_completions")
    step_template = models.ForeignKey(
        OnboardingStepTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completions",
    )
    name = models.CharField(max_length=255)
    step_type = models.CharField(max_length=40, choices=OnboardingStepTemplate.StepType.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_onboarding_steps",
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_onboarding_steps",
    )
    related_ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_steps",
    )
    document_assignment = models.ForeignKey(
        "documents.DocumentAssignment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_steps",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)
    evidence_label = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["onboarding", "id"]
        indexes = [
            models.Index(fields=["status", "step_type"]),
        ]


class StaffProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="staff_profile")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_profile",
    )
    employment_type = models.CharField(max_length=80, blank=True)
    onboarding_status = models.CharField(max_length=80, default="not_started")
    payroll_status = models.CharField(max_length=80, default="not_ready")


class SupplierProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="supplier_profile")
    supplier_code = models.CharField(max_length=80, blank=True)
    payment_status = models.CharField(max_length=80, default="not_ready")
    compliance_status = models.CharField(max_length=80, default="pending")


class PatientReferenceProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="patient_profile")
    patient_reference = models.CharField(max_length=120, unique=True)
    preferred_contact_channel = models.CharField(max_length=40, blank=True)
    masked_contact = models.CharField(max_length=120, blank=True)
    consent_status = models.CharField(max_length=80, default="unknown")


class AssetProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="asset_profile")
    asset_tag = models.CharField(max_length=120, blank=True)
    serial_number = models.CharField(max_length=120, blank=True)
    maintenance_status = models.CharField(max_length=80, default="unknown")


class InventoryItemProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="inventory_profile")
    sku = models.CharField(max_length=120, blank=True)
    barcode = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    reorder_threshold = models.PositiveIntegerField(default=0)


class AIAgentProfile(TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="ai_agent_profile")
    agent_code = models.CharField(max_length=120, unique=True)
    human_review_required = models.BooleanField(default=True)
    allowed_actions = models.JSONField(default=list, blank=True)
