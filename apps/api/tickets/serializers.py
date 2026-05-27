from rest_framework import serializers

from .models import TaskCompletion, Ticket, TicketApproval, TicketAttachment, TicketComment, TicketStatusHistory


class TicketStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = TicketStatusHistory
        fields = ["id", "from_status", "to_status", "changed_by", "changed_by_email", "note", "created_at"]


class TicketCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = TicketComment
        fields = ["id", "author", "author_email", "body", "is_internal", "created_at", "updated_at"]
        read_only_fields = ["author"]


class TicketApprovalSerializer(serializers.ModelSerializer):
    requested_by_email = serializers.CharField(source="requested_by.email", read_only=True)
    reviewed_by_email = serializers.CharField(source="reviewed_by.email", read_only=True)

    class Meta:
        model = TicketApproval
        fields = [
            "id",
            "approval_type",
            "status",
            "requested_by",
            "requested_by_email",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "decision_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["requested_by", "reviewed_by", "reviewed_at"]


class TicketAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.CharField(source="uploaded_by.email", read_only=True)

    class Meta:
        model = TicketAttachment
        fields = [
            "id",
            "uploaded_by",
            "uploaded_by_email",
            "file",
            "label",
            "content_type",
            "size_bytes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uploaded_by", "content_type", "size_bytes"]


class TaskCompletionSerializer(serializers.ModelSerializer):
    completed_by_email = serializers.CharField(source="completed_by.email", read_only=True)

    class Meta:
        model = TaskCompletion
        fields = [
            "id",
            "completed_by",
            "completed_by_email",
            "task_name",
            "task_category",
            "time_spent_minutes",
            "outcome",
            "payroll_link_approved",
            "appraisal_rating",
            "appraisal_comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "completed_by",
            "payroll_link_approved",
            "appraisal_rating",
            "appraisal_comments",
        ]


class TicketSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    related_entity_name = serializers.CharField(source="related_entity.display_name", read_only=True)
    status_history = TicketStatusHistorySerializer(many=True, read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    approvals = TicketApprovalSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    task_completion = TaskCompletionSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "category",
            "title",
            "description",
            "status",
            "priority",
            "due_at",
            "branch",
            "branch_name",
            "created_by",
            "created_by_email",
            "assigned_to",
            "assigned_to_email",
            "related_entity",
            "related_entity_name",
            "source",
            "completion_summary",
            "completed_at",
            "metadata",
            "status_history",
            "comments",
            "approvals",
            "attachments",
            "task_completion",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "ticket_number",
            "created_by",
            "completion_summary",
            "completed_at",
        ]


class TicketListSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    pending_approval_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "category",
            "title",
            "status",
            "priority",
            "due_at",
            "branch",
            "branch_name",
            "created_by_email",
            "assigned_to",
            "assigned_to_email",
            "pending_approval_count",
            "created_at",
            "updated_at",
        ]


class TicketTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)


class TicketCommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    is_internal = serializers.BooleanField(default=True)


class TicketAssignSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)


class TicketCompleteSerializer(serializers.Serializer):
    task_name = serializers.CharField(required=False, allow_blank=True)
    task_category = serializers.CharField(required=False, allow_blank=True)
    time_spent_minutes = serializers.IntegerField(default=0, min_value=0)
    outcome = serializers.CharField(required=False, allow_blank=True)
    completion_summary = serializers.CharField()
    request_approval = serializers.BooleanField(default=True)


class TicketApprovalRequestSerializer(serializers.Serializer):
    approval_type = serializers.CharField(default="ticket_completion", allow_blank=False)
    note = serializers.CharField(required=False, allow_blank=True)


class TicketApprovalDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            TicketApproval.Status.APPROVED,
            TicketApproval.Status.REJECTED,
            TicketApproval.Status.CORRECTION_REQUESTED,
        ]
    )
    decision_note = serializers.CharField(required=False, allow_blank=True)
