from django.contrib import admin

from .models import (
    AIAgentProfile,
    AssetProfile,
    Entity,
    InventoryItemProfile,
    PatientReferenceProfile,
    StaffProfile,
    SupplierProfile,
)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("display_name", "entity_type", "status", "branch", "owner_user", "responsible_user")
    list_filter = ("entity_type", "status", "branch")
    search_fields = ("display_name", "external_reference", "qr_code_value")


admin.site.register(StaffProfile)
admin.site.register(SupplierProfile)
admin.site.register(PatientReferenceProfile)
admin.site.register(AssetProfile)
admin.site.register(InventoryItemProfile)
admin.site.register(AIAgentProfile)

