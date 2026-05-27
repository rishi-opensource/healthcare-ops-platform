from rest_framework import serializers

from .models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary


class ShiftSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    staff_email = serializers.CharField(source="staff_user.email", read_only=True)
    published_by_email = serializers.CharField(source="published_by.email", read_only=True)

    class Meta:
        model = Shift
        fields = [
            "id",
            "branch",
            "branch_name",
            "staff_user",
            "staff_email",
            "role_label",
            "starts_at",
            "ends_at",
            "status",
            "notes",
            "overtime_minutes",
            "published_by",
            "published_by_email",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["published_by", "published_at"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    staff_email = serializers.CharField(source="staff_user.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    reviewed_by_email = serializers.CharField(source="reviewed_by.email", read_only=True)
    related_ticket_number = serializers.CharField(source="related_ticket.ticket_number", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "staff_user",
            "staff_email",
            "branch",
            "branch_name",
            "leave_type",
            "starts_at",
            "ends_at",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "review_note",
            "related_ticket",
            "related_ticket_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reviewed_by", "reviewed_at", "review_note", "related_ticket"]
        extra_kwargs = {
            "staff_user": {"required": False},
            "branch": {"required": False},
        }


class AttendanceRecordSerializer(serializers.ModelSerializer):
    staff_email = serializers.CharField(source="staff_user.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    shift_label = serializers.SerializerMethodField()
    approved_by_email = serializers.CharField(source="approved_by.email", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "staff_user",
            "staff_email",
            "shift",
            "shift_label",
            "branch",
            "branch_name",
            "clock_in_at",
            "clock_out_at",
            "status",
            "exception_note",
            "location_label",
            "approved_by",
            "approved_by_email",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["staff_user", "clock_in_at", "clock_out_at", "status", "approved_by", "approved_at"]

    def get_shift_label(self, obj) -> str:
        if not obj.shift:
            return ""
        return f"{obj.shift.starts_at:%Y-%m-%d %H:%M} - {obj.shift.ends_at:%H:%M}"


class HandoverNoteSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    author_email = serializers.CharField(source="author.email", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to.email", read_only=True)
    acknowledged_by_email = serializers.CharField(source="acknowledged_by.email", read_only=True)

    class Meta:
        model = HandoverNote
        fields = [
            "id",
            "branch",
            "branch_name",
            "author",
            "author_email",
            "assigned_to",
            "assigned_to_email",
            "title",
            "body",
            "status",
            "due_at",
            "acknowledged_by",
            "acknowledged_by_email",
            "acknowledged_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "acknowledged_by", "acknowledged_at"]


class TimesheetSummarySerializer(serializers.ModelSerializer):
    staff_email = serializers.CharField(source="staff_user.email", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    reviewed_by_email = serializers.CharField(source="reviewed_by.email", read_only=True)

    class Meta:
        model = TimesheetSummary
        fields = [
            "id",
            "staff_user",
            "staff_email",
            "branch",
            "branch_name",
            "period_start",
            "period_end",
            "scheduled_minutes",
            "worked_minutes",
            "task_minutes",
            "exception_count",
            "payroll_ready",
            "status",
            "submitted_at",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "review_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "scheduled_minutes",
            "worked_minutes",
            "task_minutes",
            "exception_count",
            "payroll_ready",
            "submitted_at",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]


class ReviewSerializer(serializers.Serializer):
    status = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True)


class ClockInSerializer(serializers.Serializer):
    shift = serializers.IntegerField(required=False, allow_null=True)
    location_label = serializers.CharField(required=False, allow_blank=True)


class ClockOutSerializer(serializers.Serializer):
    exception_note = serializers.CharField(required=False, allow_blank=True)


class TimesheetRefreshSerializer(serializers.Serializer):
    staff_user = serializers.IntegerField(required=False, allow_null=True)
    period_start = serializers.DateField(required=False)
    period_end = serializers.DateField(required=False)


class WorkforceSummarySerializer(serializers.Serializer):
    published_shifts = serializers.IntegerField()
    open_leave_requests = serializers.IntegerField()
    clocked_in = serializers.IntegerField()
    attendance_exceptions = serializers.IntegerField()
    open_handovers = serializers.IntegerField()
    payroll_ready = serializers.IntegerField()
    timesheets_needing_review = serializers.IntegerField()
