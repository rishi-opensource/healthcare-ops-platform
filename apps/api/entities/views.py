from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.permissions import has_role

from .models import Entity, EntityOnboarding, OnboardingStepCompletion, OnboardingWorkflowTemplate
from .serializers import (
    CompleteOnboardingStepSerializer,
    EntityCreateSerializer,
    EntityListSerializer,
    EntityOnboardingSerializer,
    EntityOnboardingSummarySerializer,
    EntitySerializer,
    EntityStatusSerializer,
    OnboardingWorkflowTemplateSerializer,
    StartOnboardingSerializer,
)
from .services import (
    activate_onboarded_entity,
    complete_onboarding_step,
    create_entity_with_profile,
    start_entity_onboarding,
    transition_entity_status,
)


class EntityViewSet(ModelViewSet):
    search_fields = ["display_name", "external_reference", "qr_code_value"]
    ordering_fields = ["display_name", "entity_type", "status", "created_at"]
    filterset_fields = ["entity_type", "status", "branch"]

    def get_serializer_class(self):
        if self.action == "list":
            return EntityListSerializer
        if self.action == "create":
            return EntityCreateSerializer
        return EntitySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Entity.objects.select_related(
                "branch",
                "owner_user",
                "responsible_user",
                "onboarding",
            )
            .prefetch_related(
                "lifecycle_events",
                "onboarding__step_completions",
                "onboarding__step_completions__related_ticket",
                "onboarding__step_completions__document_assignment__template",
            )
            .annotate(
                required_step_count=Count("onboarding__step_completions"),
                completed_step_count=Count(
                    "onboarding__step_completions",
                    filter=Q(onboarding__step_completions__status__in=["completed", "verified", "waived"]),
                ),
            )
        )
        if not user or not user.is_authenticated:
            return queryset.none()
        if has_role(user, "super_admin", "manager", "hr_payroll", "compliance", "inventory"):
            if user.primary_branch_id and not has_role(user, "super_admin"):
                queryset = queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
        else:
            queryset = queryset.filter(Q(owner_user=user) | Q(responsible_user=user))
        entity_type = self.request.query_params.get("entity_type")
        status_value = self.request.query_params.get("status")
        onboarding_status = self.request.query_params.get("onboarding_status")
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if onboarding_status:
            queryset = queryset.filter(onboarding__status=onboarding_status)
        return queryset.order_by("display_name", "id")

    def perform_create(self, serializer):
        fields = serializer.validated_data
        profile = fields.pop("profile", {})
        entity = create_entity_with_profile(
            actor_user=self.request.user,
            request=self.request,
            profile=profile,
            **fields,
        )
        serializer.instance = entity

    def perform_update(self, serializer):
        serializer.save()

    @extend_schema(request=EntityStatusSerializer, responses=EntitySerializer)
    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        entity = self.get_object()
        serializer = EntityStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = transition_entity_status(
            entity=entity,
            actor_user=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(EntitySerializer(entity, context={"request": request}).data)

    @extend_schema(request=StartOnboardingSerializer, responses=EntityOnboardingSerializer)
    @action(detail=True, methods=["post"], url_path="start-onboarding")
    def start_onboarding(self, request, pk=None):
        entity = self.get_object()
        serializer = StartOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        onboarding = start_entity_onboarding(
            entity=entity,
            actor_user=request.user,
            workflow_template_id=serializer.validated_data.get("workflow_template"),
            create_activation_ticket=serializer.validated_data["create_activation_ticket"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(EntityOnboardingSerializer(onboarding, context={"request": request}).data)

    @extend_schema(request=CompleteOnboardingStepSerializer, responses=EntityOnboardingSerializer)
    @action(detail=True, methods=["post"], url_path="complete-onboarding-step")
    def complete_onboarding_step(self, request, pk=None):
        entity = self.get_object()
        serializer = CompleteOnboardingStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        step_completion = entity.onboarding.step_completions.get(id=serializer.validated_data["step_completion"])
        complete_onboarding_step(
            step_completion=step_completion,
            actor_user=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            evidence_label=serializer.validated_data.get("evidence_label", ""),
            request=request,
        )
        entity.onboarding.refresh_from_db()
        return Response(EntityOnboardingSerializer(entity.onboarding, context={"request": request}).data)

    @extend_schema(request=EntityStatusSerializer, responses=EntitySerializer)
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        entity = self.get_object()
        serializer = EntityStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = activate_onboarded_entity(
            entity=entity,
            actor_user=request.user,
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(EntitySerializer(entity, context={"request": request}).data)

    @extend_schema(responses=EntityOnboardingSummarySerializer)
    @action(detail=False, methods=["get"])
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(
            {
                "draft": queryset.filter(status=Entity.Status.DRAFT).count(),
                "onboarding": queryset.filter(status=Entity.Status.ONBOARDING).count(),
                "active": queryset.filter(status=Entity.Status.ACTIVE).count(),
                "suspended": queryset.filter(status=Entity.Status.SUSPENDED).count(),
                "archived": queryset.filter(status=Entity.Status.ARCHIVED).count(),
                "waiting_approval": queryset.filter(
                    onboarding__status=EntityOnboarding.Status.WAITING_APPROVAL
                ).count(),
                "pending_steps": OnboardingStepCompletion.objects.filter(
                    onboarding__entity__in=queryset,
                    status=OnboardingStepCompletion.Status.PENDING,
                ).count(),
            }
        )


class OnboardingWorkflowTemplateViewSet(ReadOnlyModelViewSet):
    serializer_class = OnboardingWorkflowTemplateSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["entity_type", "name", "created_at"]
    filterset_fields = ["entity_type", "is_active"]

    def get_queryset(self):
        return OnboardingWorkflowTemplate.objects.prefetch_related("steps").annotate(step_count=Count("steps"))
