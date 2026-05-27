from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AuthLoginView, AuthLogoutView, CurrentUserView, RoleViewSet, UserViewSet
from audit.views import AuditEventViewSet
from core.views import BranchViewSet, OrganizationViewSet
from documents.views import DocumentTemplateViewSet
from entities.views import EntityViewSet, OnboardingWorkflowTemplateViewSet
from tickets.views import TicketViewSet

from .views import HealthCheckView

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("branches", BranchViewSet, basename="branch")
router.register("audit-events", AuditEventViewSet, basename="audit-event")
router.register("entities", EntityViewSet, basename="entity")
router.register(
    "onboarding-workflow-templates",
    OnboardingWorkflowTemplateViewSet,
    basename="onboarding-workflow-template",
)
router.register("tickets", TicketViewSet, basename="ticket")
router.register("document-templates", DocumentTemplateViewSet, basename="document-template")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
