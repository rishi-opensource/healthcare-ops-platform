from django.contrib import admin

from .models import (
    ConsentRecord,
    DocumentAssignment,
    DocumentFile,
    DocumentTemplate,
    TrainingAssignment,
    TrainingModule,
)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "current_version", "is_active")
    list_filter = ("template_type", "is_active")
    search_fields = ("name", "description")


@admin.register(DocumentAssignment)
class DocumentAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "assigned_to_user",
        "assigned_to_entity",
        "status",
        "due_at",
        "expires_at",
    )
    list_filter = ("status", "template__template_type")
    search_fields = ("template__name", "assigned_to_user__email", "assigned_to_entity__display_name")


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("consent_type", "subject_user", "subject_entity", "status", "expires_at")
    list_filter = ("consent_type", "status")
    search_fields = ("purpose", "subject_user__email", "subject_entity__display_name")


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "module_type", "version", "validity_days", "is_active")
    list_filter = ("module_type", "is_active")
    search_fields = ("title", "description")


@admin.register(TrainingAssignment)
class TrainingAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "module",
        "assigned_to_user",
        "assigned_to_entity",
        "status",
        "due_at",
        "expires_at",
    )
    list_filter = ("status", "module__module_type")
    search_fields = ("module__title", "assigned_to_user__email", "assigned_to_entity__display_name")


admin.site.register(DocumentFile)
