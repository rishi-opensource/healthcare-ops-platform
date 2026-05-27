from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from tickets.models import TaskCompletion, Ticket
from tickets.services import complete_ticket, create_ticket


class Phase6ReportingTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Healthcare Doctors")
        self.branch = Branch.objects.create(organization=self.organization, name="Main Clinic", code="main")
        manager_role = Role.objects.create(code=Role.Codes.MANAGER, name="Clinic Manager")
        receptionist_role = Role.objects.create(code=Role.Codes.RECEPTIONIST, name="Receptionist")
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="ChangeMe123!",
            full_name="Manager User",
            primary_branch=self.branch,
        )
        self.receptionist = User.objects.create_user(
            email="reception@example.com",
            password="ChangeMe123!",
            full_name="Reception User",
            primary_branch=self.branch,
        )
        RoleAssignment.objects.create(user=self.manager, role=manager_role, branch=self.branch)
        RoleAssignment.objects.create(user=self.receptionist, role=receptionist_role, branch=self.branch)
        self.open_ticket = create_ticket(
            actor_user=self.manager,
            title="Urgent stock warning",
            description="Check stock.",
            category=Ticket.Category.INVENTORY,
            priority=Ticket.Priority.URGENT,
            branch=self.branch,
            assigned_to=self.receptionist,
            due_at=timezone.now() - timedelta(days=1),
        )
        self.completed_ticket = create_ticket(
            actor_user=self.manager,
            title="Reception checklist",
            description="Daily checklist.",
            category=Ticket.Category.GENERAL,
            priority=Ticket.Priority.NORMAL,
            branch=self.branch,
            assigned_to=self.receptionist,
        )
        complete_ticket(
            ticket=self.completed_ticket,
            actor_user=self.receptionist,
            completion_summary="Checklist done.",
            task_name="Reception checklist",
            task_category="daily",
            time_spent_minutes=20,
            request_approval=False,
        )
        self.client = APIClient()

    def test_dashboard_report_returns_operational_aggregates(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.get("/api/v1/reports/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tickets"]["open"], 1)
        self.assertEqual(response.data["tickets"]["overdue"], 1)
        self.assertEqual(response.data["operations"]["inventory_alerts"], 1)
        self.assertEqual(response.data["workforce"]["completed_tasks"], 1)

    def test_task_review_actions_update_completion_and_audit(self):
        self.client.force_authenticate(user=self.manager)

        appraisal = self.client.post(
            f"/api/v1/tickets/{self.completed_ticket.id}/appraisal/",
            {"appraisal_rating": 4, "appraisal_comments": "Good work."},
            format="json",
        )
        payroll = self.client.post(
            f"/api/v1/tickets/{self.completed_ticket.id}/approve-payroll-link/",
            {"approved": True, "note": "Payroll ready."},
            format="json",
        )

        self.assertEqual(appraisal.status_code, 200)
        self.assertEqual(payroll.status_code, 200)
        completion = TaskCompletion.objects.get(ticket=self.completed_ticket)
        self.assertEqual(completion.appraisal_rating, 4)
        self.assertTrue(completion.payroll_link_approved)
        self.assertTrue(AuditEvent.objects.filter(action="ticket.task.appraise").exists())
        self.assertTrue(AuditEvent.objects.filter(action="ticket.task.payroll_link").exists())

    def test_user_task_summary_and_export_are_available(self):
        self.client.force_authenticate(user=self.manager)

        summary = self.client.get("/api/v1/reports/user-task-summary/")
        export = self.client.get("/api/v1/reports/export/?type=ticket_status")

        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data[0]["completed_tasks"], 1)
        self.assertEqual(summary.data[0]["total_minutes"], 20)
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export.data["report_type"], "ticket_status")

    def test_correction_request_moves_ticket_to_needs_correction(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            f"/api/v1/tickets/{self.completed_ticket.id}/request-correction/",
            {"note": "Add missing handover note."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Ticket.Status.NEEDS_CORRECTION)
        self.assertTrue(AuditEvent.objects.filter(action="ticket.correction.request").exists())
