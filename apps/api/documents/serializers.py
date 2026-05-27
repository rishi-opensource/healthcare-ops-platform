from rest_framework import serializers

from .models import ConsentRecord, DocumentAssignment, DocumentTemplate, TrainingAssignment, TrainingModule


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "description",
            "current_version",
            "is_active",
            "created_at",
            "updated_at",
        ]


class DocumentAssignmentSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    template_type = serializers.CharField(source="template.template_type", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to_user.email", read_only=True)
    assigned_to_entity_name = serializers.CharField(source="assigned_to_entity.display_name", read_only=True)
    assigned_by_email = serializers.CharField(source="assigned_by.email", read_only=True)

    class Meta:
        model = DocumentAssignment
        fields = [
            "id",
            "template",
            "template_name",
            "template_type",
            "assigned_to_user",
            "assigned_to_email",
            "assigned_to_entity",
            "assigned_to_entity_name",
            "assigned_by",
            "assigned_by_email",
            "status",
            "due_at",
            "completed_at",
            "signed_file",
            "version",
            "acknowledgement_text",
            "evidence_label",
            "expires_at",
            "renewal_ticket",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["assigned_by", "completed_at", "renewal_ticket"]


class DocumentActionSerializer(serializers.Serializer):
    acknowledgement_text = serializers.CharField(required=False, allow_blank=True)
    evidence_label = serializers.CharField(required=False, allow_blank=True)


class ConsentRecordSerializer(serializers.ModelSerializer):
    subject_user_email = serializers.CharField(source="subject_user.email", read_only=True)
    subject_entity_name = serializers.CharField(source="subject_entity.display_name", read_only=True)
    granted_by_email = serializers.CharField(source="granted_by.email", read_only=True)

    class Meta:
        model = ConsentRecord
        fields = [
            "id",
            "consent_type",
            "subject_user",
            "subject_user_email",
            "subject_entity",
            "subject_entity_name",
            "document_assignment",
            "status",
            "purpose",
            "scope",
            "granted_by",
            "granted_by_email",
            "granted_at",
            "withdrawn_at",
            "expires_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["granted_by", "granted_at", "withdrawn_at"]


class TrainingModuleSerializer(serializers.ModelSerializer):
    assignment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrainingModule
        fields = [
            "id",
            "title",
            "module_type",
            "description",
            "version",
            "validity_days",
            "quiz_required",
            "certificate_required",
            "is_active",
            "assignment_count",
            "created_at",
            "updated_at",
        ]


class TrainingAssignmentSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source="module.title", read_only=True)
    module_type = serializers.CharField(source="module.module_type", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to_user.email", read_only=True)
    assigned_to_entity_name = serializers.CharField(source="assigned_to_entity.display_name", read_only=True)
    assigned_by_email = serializers.CharField(source="assigned_by.email", read_only=True)
    reviewed_by_email = serializers.CharField(source="reviewed_by.email", read_only=True)

    class Meta:
        model = TrainingAssignment
        fields = [
            "id",
            "module",
            "module_title",
            "module_type",
            "assigned_to_user",
            "assigned_to_email",
            "assigned_to_entity",
            "assigned_to_entity_name",
            "assigned_by",
            "assigned_by_email",
            "status",
            "due_at",
            "completed_at",
            "expires_at",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "completion_note",
            "quiz_score",
            "certificate_label",
            "evidence_label",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["assigned_by", "completed_at", "expires_at", "reviewed_by", "reviewed_at"]


class TrainingCompleteSerializer(serializers.Serializer):
    completion_note = serializers.CharField(required=False, allow_blank=True)
    quiz_score = serializers.IntegerField(required=False, min_value=0, max_value=100, allow_null=True)
    evidence_label = serializers.CharField(required=False, allow_blank=True)


class TrainingReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TrainingAssignment.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)


class ComplianceSummarySerializer(serializers.Serializer):
    assigned_documents = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    signed_documents = serializers.IntegerField()
    expiring_documents = serializers.IntegerField()
    active_consents = serializers.IntegerField()
    expired_consents = serializers.IntegerField()
    assigned_training = serializers.IntegerField()
    completed_training = serializers.IntegerField()
    overdue_training = serializers.IntegerField()
    expiring_training = serializers.IntegerField()
