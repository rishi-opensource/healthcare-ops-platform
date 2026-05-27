from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsSuperAdminOrReadOnly, has_role
from audit.services import record_audit_event

from .models import (
    ConsentRecord,
    DocumentAssignment,
    DocumentTemplate,
    TrainingAssignment,
    TrainingModule,
)
from .serializers import (
    ComplianceSummarySerializer,
    ConsentRecordSerializer,
    DocumentActionSerializer,
    DocumentAssignmentSerializer,
    DocumentTemplateSerializer,
    TrainingAssignmentSerializer,
    TrainingCompleteSerializer,
    TrainingModuleSerializer,
    TrainingReviewSerializer,
)
from .services import (
    acknowledge_document,
    complete_training,
    grant_consent,
    refresh_expiry_statuses,
    review_training,
    sign_document,
    withdraw_consent,
)


def can_view_all_compliance(user) -> bool:
    return has_role(user, "super_admin", "manager", "hr_payroll", "compliance")


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


class DocumentAssignmentViewSet(ModelViewSet):
    serializer_class = DocumentAssignmentSerializer
    search_fields = ["template__name", "assigned_to_user__email", "assigned_to_entity__display_name"]
    ordering_fields = ["due_at", "expires_at", "status", "created_at"]
    filterset_fields = ["status", "template", "assigned_to_user", "assigned_to_entity"]

    def get_queryset(self):
        queryset = DocumentAssignment.objects.select_related(
            "template",
            "assigned_to_user",
            "assigned_to_entity",
            "assigned_by",
            "renewal_ticket",
        )
        user = self.request.user
        if not can_view_all_compliance(user):
            queryset = queryset.filter(Q(assigned_to_user=user) | Q(assigned_to_entity__owner_user=user))
        return queryset.order_by("status", "due_at", "-created_at")

    def perform_create(self, serializer):
        assignment = serializer.save(assigned_by=self.request.user)
        record_audit_event(
            actor_user=self.request.user,
            action="document.assignment.create",
            target=assignment,
            request=self.request,
            metadata={"template_id": assignment.template_id, "status": assignment.status},
        )

    @extend_schema(request=DocumentActionSerializer, responses=DocumentAssignmentSerializer)
    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        serializer = DocumentActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = acknowledge_document(
            assignment=self.get_object(),
            actor_user=request.user,
            acknowledgement_text=serializer.validated_data.get("acknowledgement_text", ""),
            evidence_label=serializer.validated_data.get("evidence_label", ""),
            request=request,
        )
        return Response(DocumentAssignmentSerializer(assignment, context={"request": request}).data)

    @extend_schema(request=DocumentActionSerializer, responses=DocumentAssignmentSerializer)
    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        serializer = DocumentActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = sign_document(
            assignment=self.get_object(),
            actor_user=request.user,
            acknowledgement_text=serializer.validated_data.get("acknowledgement_text", ""),
            evidence_label=serializer.validated_data.get("evidence_label", ""),
            request=request,
        )
        return Response(DocumentAssignmentSerializer(assignment, context={"request": request}).data)


class ConsentRecordViewSet(ModelViewSet):
    serializer_class = ConsentRecordSerializer
    search_fields = ["purpose", "scope", "subject_user__email", "subject_entity__display_name"]
    ordering_fields = ["granted_at", "expires_at", "status", "created_at"]
    filterset_fields = ["consent_type", "status", "subject_user", "subject_entity"]

    def get_queryset(self):
        queryset = ConsentRecord.objects.select_related(
            "subject_user",
            "subject_entity",
            "document_assignment",
            "granted_by",
        )
        user = self.request.user
        if not can_view_all_compliance(user):
            queryset = queryset.filter(Q(subject_user=user) | Q(subject_entity__owner_user=user))
        return queryset.order_by("-created_at", "-id")

    def perform_create(self, serializer):
        record = serializer.save(granted_by=self.request.user, granted_at=timezone.now())
        record_audit_event(
            actor_user=self.request.user,
            action="consent.create",
            target=record,
            request=self.request,
            metadata={"consent_type": record.consent_type, "status": record.status},
        )

    @action(detail=True, methods=["post"])
    def grant(self, request, pk=None):
        record = grant_consent(record=self.get_object(), actor_user=request.user, request=request)
        return Response(ConsentRecordSerializer(record, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        record = withdraw_consent(record=self.get_object(), actor_user=request.user, request=request)
        return Response(ConsentRecordSerializer(record, context={"request": request}).data)


class TrainingModuleViewSet(ModelViewSet):
    serializer_class = TrainingModuleSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "module_type", "created_at"]
    filterset_fields = ["module_type", "is_active"]

    def get_queryset(self):
        return TrainingModule.objects.annotate(assignment_count=Count("assignments"))

    def perform_create(self, serializer):
        module = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="training.module.create",
            target=module,
            request=self.request,
            metadata={"module_type": module.module_type},
        )

    def perform_update(self, serializer):
        module = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="training.module.update",
            target=module,
            request=self.request,
            metadata={"module_type": module.module_type},
        )


class TrainingAssignmentViewSet(ModelViewSet):
    serializer_class = TrainingAssignmentSerializer
    search_fields = ["module__title", "assigned_to_user__email", "assigned_to_entity__display_name"]
    ordering_fields = ["due_at", "expires_at", "status", "created_at"]
    filterset_fields = ["status", "module", "assigned_to_user", "assigned_to_entity"]

    def get_queryset(self):
        queryset = TrainingAssignment.objects.select_related(
            "module",
            "assigned_to_user",
            "assigned_to_entity",
            "assigned_by",
            "reviewed_by",
        )
        user = self.request.user
        if not can_view_all_compliance(user):
            queryset = queryset.filter(Q(assigned_to_user=user) | Q(assigned_to_entity__owner_user=user))
        return queryset.order_by("status", "due_at", "-created_at")

    def perform_create(self, serializer):
        assignment = serializer.save(assigned_by=self.request.user)
        record_audit_event(
            actor_user=self.request.user,
            action="training.assignment.create",
            target=assignment,
            request=self.request,
            metadata={"module_id": assignment.module_id, "status": assignment.status},
        )

    @extend_schema(request=TrainingCompleteSerializer, responses=TrainingAssignmentSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        serializer = TrainingCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = complete_training(
            assignment=self.get_object(),
            actor_user=request.user,
            completion_note=serializer.validated_data.get("completion_note", ""),
            quiz_score=serializer.validated_data.get("quiz_score"),
            evidence_label=serializer.validated_data.get("evidence_label", ""),
            request=request,
        )
        return Response(TrainingAssignmentSerializer(assignment, context={"request": request}).data)

    @extend_schema(request=TrainingReviewSerializer, responses=TrainingAssignmentSerializer)
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        serializer = TrainingReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = review_training(
            assignment=self.get_object(),
            actor_user=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(TrainingAssignmentSerializer(assignment, context={"request": request}).data)

    @extend_schema(responses=ComplianceSummarySerializer)
    @action(detail=False, methods=["get"])
    def summary(self, request):
        refresh_expiry_statuses()
        user = request.user
        documents = DocumentAssignment.objects.all()
        consents = ConsentRecord.objects.all()
        training = self.get_queryset()
        if not can_view_all_compliance(user):
            documents = documents.filter(Q(assigned_to_user=user) | Q(assigned_to_entity__owner_user=user))
            consents = consents.filter(Q(subject_user=user) | Q(subject_entity__owner_user=user))
        soon = timezone.now() + timedelta(days=30)
        return Response(
            {
                "assigned_documents": documents.count(),
                "pending_documents": documents.filter(
                    status__in=[
                        DocumentAssignment.Status.ASSIGNED,
                        DocumentAssignment.Status.VIEWED,
                    ]
                ).count(),
                "signed_documents": documents.filter(status=DocumentAssignment.Status.SIGNED).count(),
                "expiring_documents": documents.filter(expires_at__lte=soon).exclude(
                    status__in=[DocumentAssignment.Status.EXPIRED, DocumentAssignment.Status.CANCELLED]
                ).count(),
                "active_consents": consents.filter(status=ConsentRecord.Status.GIVEN).count(),
                "expired_consents": consents.filter(status=ConsentRecord.Status.EXPIRED).count(),
                "assigned_training": training.count(),
                "completed_training": training.filter(status=TrainingAssignment.Status.COMPLETED).count(),
                "overdue_training": training.filter(status=TrainingAssignment.Status.OVERDUE).count(),
                "expiring_training": training.filter(
                    expires_at__lte=soon,
                    status=TrainingAssignment.Status.COMPLETED,
                ).count(),
            }
        )
