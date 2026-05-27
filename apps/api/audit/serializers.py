from rest_framework import serializers

from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor_user.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "occurred_at",
            "actor_user",
            "actor_email",
            "actor_entity",
            "action",
            "target_type",
            "target_id",
            "branch",
            "branch_name",
            "request_id",
            "ip_address",
            "user_agent",
            "metadata",
        ]
        read_only_fields = fields

