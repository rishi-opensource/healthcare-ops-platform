from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Role, RoleAssignment, User


class RoleAssignmentInline(admin.TabularInline):
    model = RoleAssignment
    extra = 0
    autocomplete_fields = ("role", "branch")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "full_name", "primary_branch", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "mfa_required", "mfa_enrolled")
    search_fields = ("email", "full_name", "phone")
    inlines = [RoleAssignmentInline]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "phone", "primary_branch")}),
        ("Security", {"fields": ("mfa_required", "mfa_enrolled", "last_seen_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password1", "password2"),
            },
        ),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_system")
    search_fields = ("code", "name")


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch", "starts_at", "ends_at")
    list_filter = ("role", "branch")
    search_fields = ("user__email", "user__full_name", "role__code", "role__name")

