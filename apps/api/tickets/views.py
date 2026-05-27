from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import has_role

from .models import Ticket, TicketApproval
from .serializers import (
    CorrectionRequestSerializer,
    PayrollApprovalSerializer,
    TaskAppraisalSerializer,
    TaskCompletionSerializer,
    TicketApprovalDecisionSerializer,
    TicketApprovalRequestSerializer,
    TicketApprovalSerializer,
    TicketAssignSerializer,
    TicketCommentCreateSerializer,
    TicketCommentSerializer,
    TicketCompleteSerializer,
    TicketListSerializer,
    TicketSerializer,
    TicketTransitionSerializer,
)
from .services import (
    add_ticket_comment,
    appraise_task_completion,
    approve_payroll_link,
    assign_ticket,
    complete_ticket,
    create_ticket,
    request_ticket_approval,
    request_ticket_correction,
    review_ticket_approval,
    transition_ticket,
)


class TicketViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ["ticket_number", "title", "description"]
    ordering_fields = ["created_at", "due_at", "priority", "status"]
    filterset_fields = ["status", "priority", "category", "branch", "assigned_to", "related_entity"]

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        return TicketSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.select_related(
            "branch",
            "created_by",
            "assigned_to",
            "related_entity",
        ).prefetch_related("status_history", "comments", "approvals", "attachments").annotate(
            pending_approval_count=Count(
                "approvals",
                filter=Q(approvals__status=TicketApproval.Status.PENDING),
            )
        )
        if not user or not user.is_authenticated:
            return queryset.none()
        if has_role(user, "super_admin", "manager", "hr_payroll", "compliance", "inventory"):
            if user.primary_branch_id and not has_role(user, "super_admin"):
                queryset = queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
        else:
            queryset = queryset.filter(Q(created_by=user) | Q(assigned_to=user))

        status_value = self.request.query_params.get("status")
        priority_value = self.request.query_params.get("priority")
        category_value = self.request.query_params.get("category")
        assigned_to = self.request.query_params.get("assigned_to")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if priority_value:
            queryset = queryset.filter(priority=priority_value)
        if category_value:
            queryset = queryset.filter(category=category_value)
        if assigned_to == "me":
            queryset = queryset.filter(assigned_to=user)
        elif assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        return queryset.order_by("-created_at", "-id")

    def perform_create(self, serializer):
        fields = serializer.validated_data
        ticket = create_ticket(actor_user=self.request.user, request=self.request, **fields)
        serializer.instance = ticket

    @extend_schema(request=TicketTransitionSerializer, responses=TicketSerializer)
    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = transition_ticket(
            ticket=ticket,
            actor_user=request.user,
            to_status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(TicketSerializer(ticket, context={"request": request}).data)

    @extend_schema(request=TicketAssignSerializer, responses=TicketSerializer)
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assigned_to = None
        assigned_to_id = serializer.validated_data.get("assigned_to")
        if assigned_to_id:
            User = get_user_model()
            assigned_to = get_object_or_404(User, id=assigned_to_id)
        ticket = assign_ticket(
            ticket=ticket,
            actor_user=request.user,
            assigned_to=assigned_to,
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(TicketSerializer(ticket, context={"request": request}).data)

    @extend_schema(request=TicketCommentCreateSerializer, responses=TicketCommentSerializer)
    @action(detail=True, methods=["post"])
    def comments(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = add_ticket_comment(
            ticket=ticket,
            actor_user=request.user,
            body=serializer.validated_data["body"],
            is_internal=serializer.validated_data["is_internal"],
            request=request,
        )
        return Response(
            TicketCommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=TicketCompleteSerializer, responses=TicketSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = complete_ticket(
            ticket=ticket,
            actor_user=request.user,
            request=request,
            **serializer.validated_data,
        )
        return Response(TicketSerializer(ticket, context={"request": request}).data)

    @extend_schema(request=TicketApprovalRequestSerializer, responses=TicketApprovalSerializer)
    @action(detail=True, methods=["post"], url_path="request-approval")
    def request_approval(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketApprovalRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        approval = request_ticket_approval(
            ticket=ticket,
            actor_user=request.user,
            approval_type=serializer.validated_data["approval_type"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(
            TicketApprovalSerializer(approval, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[OpenApiParameter("approval_id", OpenApiTypes.INT, OpenApiParameter.PATH)],
        request=TicketApprovalDecisionSerializer,
        responses=TicketApprovalSerializer,
    )
    @action(detail=True, methods=["post"], url_path=r"approvals/(?P<approval_id>[^/.]+)/review")
    def review_approval(self, request, pk=None, approval_id=None):
        ticket = self.get_object()
        approval = ticket.approvals.get(id=approval_id)
        serializer = TicketApprovalDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        approval = review_ticket_approval(
            approval=approval,
            actor_user=request.user,
            status=serializer.validated_data["status"],
            decision_note=serializer.validated_data.get("decision_note", ""),
            request=request,
        )
        return Response(TicketApprovalSerializer(approval, context={"request": request}).data)

    @extend_schema(request=TaskAppraisalSerializer, responses=TaskCompletionSerializer)
    @action(detail=True, methods=["post"], url_path="appraisal")
    def appraisal(self, request, pk=None):
        ticket = self.get_object()
        serializer = TaskAppraisalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        completion = appraise_task_completion(
            ticket=ticket,
            actor_user=request.user,
            request=request,
            **serializer.validated_data,
        )
        return Response(TaskCompletionSerializer(completion, context={"request": request}).data)

    @extend_schema(request=PayrollApprovalSerializer, responses=TaskCompletionSerializer)
    @action(detail=True, methods=["post"], url_path="approve-payroll-link")
    def approve_payroll(self, request, pk=None):
        ticket = self.get_object()
        serializer = PayrollApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        completion = approve_payroll_link(
            ticket=ticket,
            actor_user=request.user,
            request=request,
            **serializer.validated_data,
        )
        return Response(TaskCompletionSerializer(completion, context={"request": request}).data)

    @extend_schema(request=CorrectionRequestSerializer, responses=TicketSerializer)
    @action(detail=True, methods=["post"], url_path="request-correction")
    def request_correction(self, request, pk=None):
        ticket = self.get_object()
        serializer = CorrectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = request_ticket_correction(
            ticket=ticket,
            actor_user=request.user,
            note=serializer.validated_data["note"],
            request=request,
        )
        return Response(TicketSerializer(ticket, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        counts = queryset.aggregate(
            open=Count("id", filter=Q(status=Ticket.Status.OPEN)),
            in_progress=Count("id", filter=Q(status=Ticket.Status.IN_PROGRESS)),
            waiting_approval=Count("id", filter=Q(status=Ticket.Status.WAITING_APPROVAL)),
            needs_correction=Count("id", filter=Q(status=Ticket.Status.NEEDS_CORRECTION)),
            completed=Count("id", filter=Q(status=Ticket.Status.COMPLETED)),
            urgent=Count("id", filter=Q(priority=Ticket.Priority.URGENT)),
            assigned_to_me=Count("id", filter=Q(assigned_to=request.user)),
        )
        return Response(counts)

    @action(detail=False, methods=["get"], url_path="task-summary")
    def task_summary(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(task_completion__isnull=False)
        rows = (
            queryset.values(
                "task_completion__completed_by",
                "task_completion__completed_by__email",
            )
            .annotate(
                completed_tasks=Count("id"),
                payroll_ready=Count("id", filter=Q(task_completion__payroll_link_approved=True)),
                corrections=Count("id", filter=Q(status=Ticket.Status.NEEDS_CORRECTION)),
            )
            .order_by("task_completion__completed_by__email")
        )
        return Response(
            [
                {
                    "user_id": row["task_completion__completed_by"],
                    "email": row["task_completion__completed_by__email"],
                    "completed_tasks": row["completed_tasks"],
                    "payroll_ready": row["payroll_ready"],
                    "corrections": row["corrections"],
                }
                for row in rows
            ]
        )
