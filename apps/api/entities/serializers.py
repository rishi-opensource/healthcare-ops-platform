from rest_framework import serializers

from .models import (
    AIAgentProfile,
    AssetProfile,
    Entity,
    EntityLifecycleEvent,
    EntityOnboarding,
    InventoryItemProfile,
    OnboardingStepCompletion,
    OnboardingStepTemplate,
    OnboardingWorkflowTemplate,
    PatientReferenceProfile,
    StaffProfile,
    SupplierProfile,
)


class StaffProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "id",
            "user",
            "user_email",
            "employment_type",
            "onboarding_status",
            "payroll_status",
            "created_at",
            "updated_at",
        ]


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        fields = ["id", "supplier_code", "payment_status", "compliance_status", "created_at", "updated_at"]


class PatientReferenceProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientReferenceProfile
        fields = [
            "id",
            "patient_reference",
            "preferred_contact_channel",
            "masked_contact",
            "consent_status",
            "created_at",
            "updated_at",
        ]


class AssetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetProfile
        fields = ["id", "asset_tag", "serial_number", "maintenance_status", "created_at", "updated_at"]


class InventoryItemProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItemProfile
        fields = ["id", "sku", "barcode", "unit", "reorder_threshold", "created_at", "updated_at"]


class AIAgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAgentProfile
        fields = ["id", "agent_code", "human_review_required", "allowed_actions", "created_at", "updated_at"]


class EntityLifecycleEventSerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = EntityLifecycleEvent
        fields = ["id", "from_status", "to_status", "changed_by", "changed_by_email", "note", "created_at"]


class OnboardingWorkflowTemplateSerializer(serializers.ModelSerializer):
    step_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = OnboardingWorkflowTemplate
        fields = ["id", "entity_type", "name", "description", "is_active", "step_count", "created_at", "updated_at"]


class OnboardingStepTemplateSerializer(serializers.ModelSerializer):
    document_template_name = serializers.CharField(source="document_template.name", read_only=True)

    class Meta:
        model = OnboardingStepTemplate
        fields = [
            "id",
            "workflow_template",
            "name",
            "step_type",
            "order",
            "is_required",
            "document_template",
            "document_template_name",
            "ticket_category",
            "metadata",
            "created_at",
            "updated_at",
        ]


class OnboardingStepCompletionSerializer(serializers.ModelSerializer):
    completed_by_email = serializers.CharField(source="completed_by.email", read_only=True)
    verified_by_email = serializers.CharField(source="verified_by.email", read_only=True)
    related_ticket_number = serializers.CharField(source="related_ticket.ticket_number", read_only=True)
    document_template_name = serializers.CharField(
        source="document_assignment.template.name",
        read_only=True,
    )

    class Meta:
        model = OnboardingStepCompletion
        fields = [
            "id",
            "step_template",
            "name",
            "step_type",
            "status",
            "completed_by",
            "completed_by_email",
            "verified_by",
            "verified_by_email",
            "related_ticket",
            "related_ticket_number",
            "document_assignment",
            "document_template_name",
            "completed_at",
            "verified_at",
            "note",
            "evidence_label",
            "metadata",
            "created_at",
            "updated_at",
        ]


class EntityOnboardingSerializer(serializers.ModelSerializer):
    workflow_template_name = serializers.CharField(source="workflow_template.name", read_only=True)
    started_by_email = serializers.CharField(source="started_by.email", read_only=True)
    completed_by_email = serializers.CharField(source="completed_by.email", read_only=True)
    activation_ticket_number = serializers.CharField(source="activation_ticket.ticket_number", read_only=True)
    step_completions = OnboardingStepCompletionSerializer(many=True, read_only=True)
    required_step_count = serializers.IntegerField(read_only=True)
    completed_step_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = EntityOnboarding
        fields = [
            "id",
            "workflow_template",
            "workflow_template_name",
            "status",
            "started_by",
            "started_by_email",
            "completed_by",
            "completed_by_email",
            "started_at",
            "completed_at",
            "activation_ticket",
            "activation_ticket_number",
            "required_step_count",
            "completed_step_count",
            "step_completions",
            "metadata",
            "created_at",
            "updated_at",
        ]


class EntitySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    owner_email = serializers.CharField(source="owner_user.email", read_only=True)
    responsible_email = serializers.CharField(source="responsible_user.email", read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)
    supplier_profile = SupplierProfileSerializer(read_only=True)
    patient_profile = PatientReferenceProfileSerializer(read_only=True)
    asset_profile = AssetProfileSerializer(read_only=True)
    inventory_profile = InventoryItemProfileSerializer(read_only=True)
    ai_agent_profile = AIAgentProfileSerializer(read_only=True)
    onboarding = EntityOnboardingSerializer(read_only=True)
    lifecycle_events = EntityLifecycleEventSerializer(many=True, read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "entity_type",
            "display_name",
            "status",
            "branch",
            "branch_name",
            "owner_user",
            "owner_email",
            "responsible_user",
            "responsible_email",
            "external_reference",
            "qr_code_value",
            "metadata",
            "staff_profile",
            "supplier_profile",
            "patient_profile",
            "asset_profile",
            "inventory_profile",
            "ai_agent_profile",
            "onboarding",
            "lifecycle_events",
            "created_at",
            "updated_at",
        ]


class EntityListSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    responsible_email = serializers.CharField(source="responsible_user.email", read_only=True)
    onboarding_status = serializers.CharField(source="onboarding.status", read_only=True)
    completed_step_count = serializers.IntegerField(read_only=True)
    required_step_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "entity_type",
            "display_name",
            "status",
            "branch",
            "branch_name",
            "responsible_user",
            "responsible_email",
            "external_reference",
            "qr_code_value",
            "onboarding_status",
            "completed_step_count",
            "required_step_count",
            "created_at",
            "updated_at",
        ]


class EntityCreateSerializer(serializers.ModelSerializer):
    profile = serializers.DictField(required=False, write_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "entity_type",
            "display_name",
            "status",
            "branch",
            "owner_user",
            "responsible_user",
            "external_reference",
            "qr_code_value",
            "metadata",
            "profile",
        ]


class EntityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Entity.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)


class StartOnboardingSerializer(serializers.Serializer):
    workflow_template = serializers.IntegerField(required=False, allow_null=True)
    create_activation_ticket = serializers.BooleanField(default=True)
    note = serializers.CharField(required=False, allow_blank=True)


class CompleteOnboardingStepSerializer(serializers.Serializer):
    step_completion = serializers.IntegerField()
    status = serializers.ChoiceField(choices=OnboardingStepCompletion.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)
    evidence_label = serializers.CharField(required=False, allow_blank=True)


class EntityOnboardingSummarySerializer(serializers.Serializer):
    draft = serializers.IntegerField()
    onboarding = serializers.IntegerField()
    active = serializers.IntegerField()
    suspended = serializers.IntegerField()
    archived = serializers.IntegerField()
    waiting_approval = serializers.IntegerField()
    pending_steps = serializers.IntegerField()
