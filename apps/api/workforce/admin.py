from django.contrib import admin

from .models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("staff_user", "branch", "starts_at", "ends_at", "status", "overtime_minutes")
    list_filter = ("status", "branch")
    search_fields = ("staff_user__email", "role_label", "notes")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("staff_user", "leave_type", "starts_at", "ends_at", "status")
    list_filter = ("status", "leave_type", "branch")
    search_fields = ("staff_user__email", "reason")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("staff_user", "branch", "clock_in_at", "clock_out_at", "status")
    list_filter = ("status", "branch")
    search_fields = ("staff_user__email", "exception_note", "location_label")


@admin.register(HandoverNote)
class HandoverNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "branch", "author", "assigned_to", "status", "due_at")
    list_filter = ("status", "branch")
    search_fields = ("title", "body", "author__email", "assigned_to__email")


@admin.register(TimesheetSummary)
class TimesheetSummaryAdmin(admin.ModelAdmin):
    list_display = ("staff_user", "period_start", "period_end", "status", "payroll_ready")
    list_filter = ("status", "payroll_ready", "branch")
    search_fields = ("staff_user__email", "review_note")
