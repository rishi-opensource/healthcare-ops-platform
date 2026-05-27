from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsSuperAdminOrReadOnly
from audit.services import record_audit_event

from .models import DocumentTemplate
from .serializers import DocumentTemplateSerializer


class DocumentTemplateViewSet(ModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "template_type", "created_at"]
    filterset_fields = ["template_type", "is_active"]

    def perform_create(self, serializer):
        template = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="document_template.create",
            target=template,
            request=self.request,
        )

    def perform_update(self, serializer):
        template = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="document_template.update",
            target=template,
            request=self.request,
        )

