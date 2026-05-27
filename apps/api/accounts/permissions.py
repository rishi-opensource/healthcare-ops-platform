from rest_framework.permissions import SAFE_METHODS, BasePermission


def has_role(user, *role_codes: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role_assignments.filter(role__code__in=role_codes, ends_at__isnull=True).exists()


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return has_role(request.user, "super_admin")


class IsSuperAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return has_role(request.user, "super_admin")


class IsManagerOrSuperAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return has_role(request.user, "super_admin", "manager")


class IsSelfOrPrivileged(BasePermission):
    privileged_roles = {"super_admin", "manager", "hr_payroll", "compliance"}

    def has_object_permission(self, request, view, obj) -> bool:
        if has_role(request.user, *self.privileged_roles):
            return True
        return getattr(obj, "id", None) == getattr(request.user, "id", None)

