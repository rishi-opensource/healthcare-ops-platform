from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AuthLoginView, AuthLogoutView, CurrentUserView, RoleViewSet, UserViewSet
from audit.views import AuditEventViewSet
from core.views import BranchViewSet, OrganizationViewSet
from documents.views import (
    ConsentRecordViewSet,
    DocumentAssignmentViewSet,
    DocumentTemplateViewSet,
    TrainingAssignmentViewSet,
    TrainingModuleViewSet,
)
from entities.views import EntityViewSet, OnboardingWorkflowTemplateViewSet
from inventory.views import (
    BarcodeAliasViewSet,
    DeliveryReceiptViewSet,
    InventoryBatchViewSet,
    InventorySummaryViewSet,
    PurchaseOrderViewSet,
    StockItemViewSet,
)
from tickets.views import TicketViewSet
from workforce.views import (
    AttendanceRecordViewSet,
    HandoverNoteViewSet,
    LeaveRequestViewSet,
    ShiftViewSet,
    TimesheetSummaryViewSet,
)

from .views import DashboardReportView, HealthCheckView, ReportExportView, UserTaskSummaryView

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
router.register("document-assignments", DocumentAssignmentViewSet, basename="document-assignment")
router.register("consent-records", ConsentRecordViewSet, basename="consent-record")
router.register("training-modules", TrainingModuleViewSet, basename="training-module")
router.register("training-assignments", TrainingAssignmentViewSet, basename="training-assignment")
router.register("shifts", ShiftViewSet, basename="shift")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")
router.register("attendance-records", AttendanceRecordViewSet, basename="attendance-record")
router.register("handover-notes", HandoverNoteViewSet, basename="handover-note")
router.register("timesheet-summaries", TimesheetSummaryViewSet, basename="timesheet-summary")
router.register("stock-items", StockItemViewSet, basename="stock-item")
router.register("inventory-batches", InventoryBatchViewSet, basename="inventory-batch")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register("delivery-receipts", DeliveryReceiptViewSet, basename="delivery-receipt")
router.register("barcode-aliases", BarcodeAliasViewSet, basename="barcode-alias")
router.register("inventory-summary", InventorySummaryViewSet, basename="inventory-summary")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("reports/dashboard/", DashboardReportView.as_view(), name="reports-dashboard"),
    path("reports/user-task-summary/", UserTaskSummaryView.as_view(), name="reports-user-task-summary"),
    path("reports/export/", ReportExportView.as_view(), name="reports-export"),
    path("", include(router.urls)),
]
