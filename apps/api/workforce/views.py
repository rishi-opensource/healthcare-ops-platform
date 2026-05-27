from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import has_role
from audit.services import record_audit_event

from .models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary
from .serializers import (
    AttendanceRecordSerializer,
    ClockInSerializer,
    ClockOutSerializer,
    HandoverNoteSerializer,
    LeaveRequestSerializer,
    ReviewSerializer,
    ShiftSerializer,
    TimesheetRefreshSerializer,
    TimesheetSummarySerializer,
    WorkforceSummarySerializer,
)
from .services import (
    acknowledge_handover,
    approve_attendance,
    clock_in,
    clock_out,
    default_pay_period,
    publish_shift,
    refresh_timesheet_summary,
    review_leave_request,
    review_timesheet,
    submit_timesheet,
)


def can_manage_workforce(user) -> bool:
    return has_role(user, "super_admin", "manager", "hr_payroll")


def staff_filter(queryset, user, user_field="staff_user"):
    if can_manage_workforce(user):
        if user.primary_branch_id and not has_role(user, "super_admin"):
            return queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
        return queryset
    return queryset.filter(**{user_field: user})


class ShiftViewSet(ModelViewSet):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "staff_user"]
    search_fields = ["staff_user__email", "role_label", "notes"]
    ordering_fields = ["starts_at", "ends_at", "status"]

    def get_queryset(self):
        return staff_filter(
            Shift.objects.select_related("branch", "staff_user", "published_by"),
            self.request.user,
        )

    def perform_create(self, serializer):
        shift = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="workforce.shift.create",
            target=shift,
            request=self.request,
        )

    @extend_schema(responses=ShiftSerializer)
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        shift = publish_shift(shift=self.get_object(), actor_user=request.user, request=request)
        return Response(ShiftSerializer(shift, context={"request": request}).data)


class LeaveRequestViewSet(ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "leave_type", "branch", "staff_user"]
    ordering_fields = ["starts_at", "ends_at", "status", "created_at"]

    def get_queryset(self):
        return staff_filter(
            LeaveRequest.objects.select_related("staff_user", "branch", "reviewed_by", "related_ticket"),
            self.request.user,
        )

    def perform_create(self, serializer):
        staff_user = serializer.validated_data.get("staff_user") or self.request.user
        if not can_manage_workforce(self.request.user):
            staff_user = self.request.user
        leave_request = serializer.save(
            staff_user=staff_user,
            branch=serializer.validated_data.get("branch") or staff_user.primary_branch,
        )
        record_audit_event(
            actor_user=self.request.user,
            action="workforce.leave.create",
            target=leave_request,
            request=self.request,
        )

    @extend_schema(request=ReviewSerializer, responses=LeaveRequestSerializer)
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = review_leave_request(
            leave_request=self.get_object(),
            actor_user=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(LeaveRequestSerializer(leave_request, context={"request": request}).data)


class AttendanceRecordViewSet(ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "staff_user", "shift"]
    ordering_fields = ["clock_in_at", "clock_out_at", "status"]

    def get_queryset(self):
        return staff_filter(
            AttendanceRecord.objects.select_related("staff_user", "shift", "branch", "approved_by"),
            self.request.user,
        )

    @extend_schema(request=ClockInSerializer, responses=AttendanceRecordSerializer)
    @action(detail=False, methods=["post"], url_path="clock-in")
    def clock_in(self, request):
        serializer = ClockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift = None
        if serializer.validated_data.get("shift"):
            shift = Shift.objects.get(id=serializer.validated_data["shift"])
        record = clock_in(
            actor_user=request.user,
            shift=shift,
            location_label=serializer.validated_data.get("location_label", ""),
            request=request,
        )
        return Response(AttendanceRecordSerializer(record, context={"request": request}).data)

    @extend_schema(request=ClockOutSerializer, responses=AttendanceRecordSerializer)
    @action(detail=True, methods=["post"], url_path="clock-out")
    def clock_out(self, request, pk=None):
        serializer = ClockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = clock_out(
            record=self.get_object(),
            actor_user=request.user,
            exception_note=serializer.validated_data.get("exception_note", ""),
            request=request,
        )
        return Response(AttendanceRecordSerializer(record, context={"request": request}).data)

    @extend_schema(responses=AttendanceRecordSerializer)
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        record = approve_attendance(record=self.get_object(), actor_user=request.user, request=request)
        return Response(AttendanceRecordSerializer(record, context={"request": request}).data)


class HandoverNoteViewSet(ModelViewSet):
    serializer_class = HandoverNoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "assigned_to"]
    ordering_fields = ["due_at", "status", "created_at"]

    def get_queryset(self):
        queryset = HandoverNote.objects.select_related("branch", "author", "assigned_to", "acknowledged_by")
        if can_manage_workforce(self.request.user):
            if self.request.user.primary_branch_id and not has_role(self.request.user, "super_admin"):
                return queryset.filter(branch=self.request.user.primary_branch)
            return queryset
        return queryset.filter(Q(author=self.request.user) | Q(assigned_to=self.request.user))

    def perform_create(self, serializer):
        note = serializer.save(author=self.request.user)
        record_audit_event(
            actor_user=self.request.user,
            action="workforce.handover.create",
            target=note,
            request=self.request,
        )

    @extend_schema(responses=HandoverNoteSerializer)
    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        note = acknowledge_handover(note=self.get_object(), actor_user=request.user, request=request)
        return Response(HandoverNoteSerializer(note, context={"request": request}).data)


class TimesheetSummaryViewSet(ModelViewSet):
    serializer_class = TimesheetSummarySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "staff_user", "payroll_ready"]
    ordering_fields = ["period_start", "period_end", "status"]

    def get_queryset(self):
        return staff_filter(
            TimesheetSummary.objects.select_related("staff_user", "branch", "reviewed_by"),
            self.request.user,
        )

    @extend_schema(request=TimesheetRefreshSerializer, responses=TimesheetSummarySerializer)
    @action(detail=False, methods=["post"])
    def refresh(self, request):
        serializer = TimesheetRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User = get_user_model()
        staff_user = request.user
        if serializer.validated_data.get("staff_user") and can_manage_workforce(request.user):
            staff_user = User.objects.get(id=serializer.validated_data["staff_user"])
        period_start = serializer.validated_data.get("period_start")
        period_end = serializer.validated_data.get("period_end")
        if not period_start or not period_end:
            period_start, period_end = default_pay_period()
        summary = refresh_timesheet_summary(
            staff_user=staff_user,
            period_start=period_start,
            period_end=period_end,
            actor_user=request.user,
            request=request,
        )
        return Response(TimesheetSummarySerializer(summary, context={"request": request}).data)

    @extend_schema(responses=TimesheetSummarySerializer)
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        summary = submit_timesheet(summary=self.get_object(), actor_user=request.user, request=request)
        return Response(TimesheetSummarySerializer(summary, context={"request": request}).data)

    @extend_schema(request=ReviewSerializer, responses=TimesheetSummarySerializer)
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summary = review_timesheet(
            summary=self.get_object(),
            actor_user=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("note", ""),
            request=request,
        )
        return Response(TimesheetSummarySerializer(summary, context={"request": request}).data)

    @extend_schema(responses=WorkforceSummarySerializer)
    @action(detail=False, methods=["get"])
    def summary(self, request):
        now = timezone.now()
        shifts = staff_filter(Shift.objects.all(), request.user)
        leave = staff_filter(LeaveRequest.objects.all(), request.user)
        attendance = staff_filter(AttendanceRecord.objects.all(), request.user)
        handovers = HandoverNote.objects.all()
        if not can_manage_workforce(request.user):
            handovers = handovers.filter(Q(author=request.user) | Q(assigned_to=request.user))
        elif request.user.primary_branch_id and not has_role(request.user, "super_admin"):
            handovers = handovers.filter(branch=request.user.primary_branch)
        timesheets = staff_filter(TimesheetSummary.objects.all(), request.user)
        return Response(
            {
                "published_shifts": shifts.filter(status=Shift.Status.PUBLISHED, starts_at__gte=now).count(),
                "open_leave_requests": leave.filter(status=LeaveRequest.Status.REQUESTED).count(),
                "clocked_in": attendance.filter(status=AttendanceRecord.Status.CLOCKED_IN).count(),
                "attendance_exceptions": attendance.filter(status=AttendanceRecord.Status.EXCEPTION).count(),
                "open_handovers": handovers.filter(status=HandoverNote.Status.OPEN).count(),
                "payroll_ready": timesheets.filter(payroll_ready=True).count(),
                "timesheets_needing_review": timesheets.filter(status=TimesheetSummary.Status.SUBMITTED).count(),
            }
        )
