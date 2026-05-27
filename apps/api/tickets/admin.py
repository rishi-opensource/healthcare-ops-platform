from django.contrib import admin

from .models import (
    TaskCompletion,
    Ticket,
    TicketApproval,
    TicketAttachment,
    TicketComment,
    TicketLink,
    TicketStatusHistory,
)


class TicketStatusHistoryInline(admin.TabularInline):
    model = TicketStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "note", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "title", "category", "status", "priority", "assigned_to", "branch")
    list_filter = ("category", "status", "priority", "branch")
    search_fields = ("ticket_number", "title", "description")
    inlines = [TicketStatusHistoryInline]


admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
admin.site.register(TicketApproval)
admin.site.register(TaskCompletion)
admin.site.register(TicketLink)

