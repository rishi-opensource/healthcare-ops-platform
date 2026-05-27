from django.contrib import admin

from .models import DocumentAssignment, DocumentFile, DocumentTemplate


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "current_version", "is_active")
    list_filter = ("template_type", "is_active")
    search_fields = ("name", "description")


admin.site.register(DocumentFile)
admin.site.register(DocumentAssignment)

