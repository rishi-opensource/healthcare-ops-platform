from rest_framework.viewsets import ReadOnlyModelViewSet

from accounts.permissions import has_role

from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditEventSerializer
    search_fields = ["action", "target_type", "target_id", "actor_user__email"]
    ordering_fields = ["occurred_at", "action"]

    def get_queryset(self):
        user = self.request.user
        queryset = AuditEvent.objects.select_related("actor_user", "branch", "actor_entity")
        if not user or not user.is_authenticated:
            return queryset.none()
        if has_role(user, "super_admin", "compliance"):
            return queryset
        return queryset.filter(actor_user=user)
