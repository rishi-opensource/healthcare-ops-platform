from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import has_role
from documents.models import ConsentRecord, DocumentAssignment, TrainingAssignment
from documents.services import refresh_expiry_statuses
from entities.models import Entity, EntityOnboarding, OnboardingStepCompletion
from tickets.models import TaskCompletion, Ticket, TicketApproval


def privileged_report_user(user) -> bool:
    return has_role(user, "super_admin", "manager", "hr_payroll", "compliance", "inventory")


def visible_tickets(user):
    queryset = Ticket.objects.all()
    if not privileged_report_user(user):
        return queryset.filter(Q(created_by=user) | Q(assigned_to=user))
    if user.primary_branch_id and not has_role(user, "super_admin"):
        return queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
    return queryset


def visible_entities(user):
    queryset = Entity.objects.all()
    if not privileged_report_user(user):
        return queryset.filter(Q(owner_user=user) | Q(responsible_user=user))
    if user.primary_branch_id and not has_role(user, "super_admin"):
        return queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
    return queryset


def visible_documents(user):
    queryset = DocumentAssignment.objects.all()
    if not privileged_report_user(user):
        return queryset.filter(Q(assigned_to_user=user) | Q(assigned_to_entity__owner_user=user))
    return queryset


def visible_training(user):
    queryset = TrainingAssignment.objects.all()
    if not privileged_report_user(user):
        return queryset.filter(Q(assigned_to_user=user) | Q(assigned_to_entity__owner_user=user))
    return queryset


def visible_consents(user):
    queryset = ConsentRecord.objects.all()
    if not privileged_report_user(user):
        return queryset.filter(Q(subject_user=user) | Q(subject_entity__owner_user=user))
    return queryset


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        responses=inline_serializer(
            name="HealthCheckResponse",
            fields={
                "status": serializers.CharField(),
                "service": serializers.CharField(),
                "version": serializers.CharField(),
            },
        )
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "healthcare-doctors-api",
                "version": "0.1.0",
            }
        )


class DashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="DashboardReportResponse",
            fields={
                "generated_at": serializers.DateTimeField(),
                "scope": serializers.CharField(),
                "tickets": serializers.JSONField(),
                "entities": serializers.JSONField(),
                "workforce": serializers.JSONField(),
                "operations": serializers.JSONField(),
                "compliance": serializers.JSONField(),
                "daily_workspace": serializers.JSONField(),
            },
        )
    )
    def get(self, request):
        refresh_expiry_statuses()
        now = timezone.now()
        soon = now + timedelta(days=30)
        tickets = visible_tickets(request.user)
        entities = visible_entities(request.user)
        documents = visible_documents(request.user)
        training = visible_training(request.user)
        consents = visible_consents(request.user)
        task_completions = TaskCompletion.objects.filter(ticket__in=tickets)
        active_statuses = [Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS, Ticket.Status.WAITING_APPROVAL]
        return Response(
            {
                "generated_at": now,
                "scope": "all" if has_role(request.user, "super_admin") else "permitted",
                "tickets": {
                    "open": tickets.filter(status=Ticket.Status.OPEN).count(),
                    "in_progress": tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
                    "waiting_approval": tickets.filter(status=Ticket.Status.WAITING_APPROVAL).count(),
                    "needs_correction": tickets.filter(status=Ticket.Status.NEEDS_CORRECTION).count(),
                    "completed": tickets.filter(status=Ticket.Status.COMPLETED).count(),
                    "overdue": tickets.filter(due_at__lt=now).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "urgent": tickets.filter(priority=Ticket.Priority.URGENT).exclude(
                        status__in=[Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "pending_approvals": TicketApproval.objects.filter(
                        ticket__in=tickets,
                        status=TicketApproval.Status.PENDING,
                    ).count(),
                },
                "entities": {
                    "active": entities.filter(status=Entity.Status.ACTIVE).count(),
                    "onboarding": entities.filter(status=Entity.Status.ONBOARDING).count(),
                    "pending_onboarding_steps": OnboardingStepCompletion.objects.filter(
                        onboarding__entity__in=entities,
                        status__in=[
                            OnboardingStepCompletion.Status.PENDING,
                            OnboardingStepCompletion.Status.NEEDS_CORRECTION,
                        ],
                    ).count(),
                    "waiting_onboarding_approval": EntityOnboarding.objects.filter(
                        entity__in=entities,
                        status=EntityOnboarding.Status.WAITING_APPROVAL,
                    ).count(),
                },
                "workforce": {
                    "users_working": User.objects.filter(
                        Q(assigned_tickets__in=tickets.filter(status__in=active_statuses))
                        | Q(task_completions__ticket__in=tickets.filter(completed_at__date=now.date()))
                    )
                    .distinct()
                    .count(),
                    "completed_tasks": task_completions.count(),
                    "payroll_ready": task_completions.filter(payroll_link_approved=True).count(),
                    "appraisal_feedback_pending": task_completions.filter(appraisal_rating__isnull=True).count(),
                },
                "operations": {
                    "payroll_pending": tickets.filter(category=Ticket.Category.PAYROLL).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "leave_pending": tickets.filter(category=Ticket.Category.LEAVE).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "inventory_alerts": tickets.filter(category=Ticket.Category.INVENTORY).filter(
                        Q(priority=Ticket.Priority.HIGH) | Q(priority=Ticket.Priority.URGENT)
                    ).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "incidents_open": tickets.filter(category=Ticket.Category.INCIDENT).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "ai_review_pending": tickets.filter(category=Ticket.Category.AI_CREATED).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                },
                "compliance": {
                    "pending_documents": documents.filter(
                        status__in=[DocumentAssignment.Status.ASSIGNED, DocumentAssignment.Status.VIEWED]
                    ).count(),
                    "signed_documents": documents.filter(status=DocumentAssignment.Status.SIGNED).count(),
                    "expiring_documents": documents.filter(expires_at__lte=soon).exclude(
                        status__in=[DocumentAssignment.Status.EXPIRED, DocumentAssignment.Status.CANCELLED]
                    ).count(),
                    "active_consents": consents.filter(status=ConsentRecord.Status.GIVEN).count(),
                    "overdue_training": training.filter(status=TrainingAssignment.Status.OVERDUE).count(),
                    "expiring_training": training.filter(
                        status=TrainingAssignment.Status.COMPLETED,
                        expires_at__lte=soon,
                    ).count(),
                },
                "daily_workspace": {
                    "due_today": tickets.filter(due_at__date=now.date()).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "handover": tickets.filter(
                        Q(metadata__handover=True) | Q(category=Ticket.Category.GENERAL, priority=Ticket.Priority.HIGH)
                    ).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "stock_warnings": tickets.filter(category=Ticket.Category.INVENTORY).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                    "pending_approvals": TicketApproval.objects.filter(
                        ticket__in=tickets,
                        status=TicketApproval.Status.PENDING,
                    ).count(),
                    "communication_followups": tickets.filter(category=Ticket.Category.APPOINTMENT).exclude(
                        status__in=[Ticket.Status.COMPLETED, Ticket.Status.CLOSED, Ticket.Status.CANCELLED]
                    ).count(),
                },
            }
        )


class UserTaskSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="UserTaskSummaryResponse",
            many=True,
            fields={
                "user_id": serializers.IntegerField(allow_null=True),
                "email": serializers.CharField(allow_null=True),
                "full_name": serializers.CharField(allow_null=True),
                "completed_tasks": serializers.IntegerField(),
                "total_minutes": serializers.IntegerField(),
                "payroll_ready": serializers.IntegerField(),
                "correction_requests": serializers.IntegerField(),
                "appraisal_feedback": serializers.IntegerField(),
            },
        )
    )
    def get(self, request):
        tickets = visible_tickets(request.user)
        rows = (
            TaskCompletion.objects.filter(ticket__in=tickets)
            .values("completed_by", "completed_by__email", "completed_by__full_name")
            .annotate(
                completed_tasks=Count("id"),
                total_minutes=Sum("time_spent_minutes"),
                payroll_ready=Count("id", filter=Q(payroll_link_approved=True)),
                correction_requests=Count("id", filter=Q(ticket__status=Ticket.Status.NEEDS_CORRECTION)),
                appraisal_feedback=Count("id", filter=Q(appraisal_rating__isnull=False)),
            )
            .order_by("completed_by__email")
        )
        return Response(
            [
                {
                    "user_id": row["completed_by"],
                    "email": row["completed_by__email"],
                    "full_name": row["completed_by__full_name"],
                    "completed_tasks": row["completed_tasks"],
                    "total_minutes": row["total_minutes"] or 0,
                    "payroll_ready": row["payroll_ready"],
                    "correction_requests": row["correction_requests"],
                    "appraisal_feedback": row["appraisal_feedback"],
                }
                for row in rows
            ]
        )


class ReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="ReportExportResponse",
            fields={
                "report_type": serializers.CharField(),
                "generated_at": serializers.DateTimeField(),
                "rows": serializers.ListField(child=serializers.JSONField()),
            },
        )
    )
    def get(self, request):
        report_type = request.query_params.get("type", "ticket_status")
        tickets = visible_tickets(request.user)
        if report_type == "user_tasks":
            rows = UserTaskSummaryView().get(request).data
        else:
            rows = list(
                tickets.values("status")
                .annotate(count=Count("id"))
                .order_by("status")
            )
        return Response({"report_type": report_type, "generated_at": timezone.now(), "rows": rows})
