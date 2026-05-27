from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from tickets.models import Ticket, TicketApproval, TicketComment


class Phase3TicketVerticalSliceTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Healthcare Doctors")
        self.branch = Branch.objects.create(organization=self.organization, name="Main Clinic", code="main")
        self.other_branch = Branch.objects.create(organization=self.organization, name="North Clinic", code="north")
        manager_role = Role.objects.create(code=Role.Codes.MANAGER, name="Clinic Manager")
        receptionist_role = Role.objects.create(code=Role.Codes.RECEPTIONIST, name="Receptionist")
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="ChangeMe123!",
            full_name="Manager User",
            primary_branch=self.branch,
        )
        self.assignee = User.objects.create_user(
            email="assignee@example.com",
            password="ChangeMe123!",
            full_name="Assignee User",
            primary_branch=self.branch,
        )
        self.out_of_branch_user = User.objects.create_user(
            email="north@example.com",
            password="ChangeMe123!",
            full_name="North User",
            primary_branch=self.other_branch,
        )
        RoleAssignment.objects.create(user=self.manager, role=manager_role, branch=self.branch)
        RoleAssignment.objects.create(user=self.assignee, role=receptionist_role, branch=self.branch)
        self.client = APIClient()

    def test_ticket_lifecycle_creates_timeline_approval_and_audit_events(self):
        self.client.force_authenticate(user=self.manager)
        create_response = self.client.post(
            "/api/v1/tickets/",
            {
                "title": "Prepare flu clinic",
                "description": "Confirm room, signage, and supplies.",
                "category": "appointment",
                "priority": "high",
                "branch": self.branch.id,
                "assigned_to": self.assignee.id,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        ticket_id = create_response.data["id"]

        assign_response = self.client.post(
            f"/api/v1/tickets/{ticket_id}/assign/",
            {"assigned_to": self.assignee.id, "note": "Reception to coordinate."},
            format="json",
        )
        self.assertEqual(assign_response.status_code, 200)

        comment_response = self.client.post(
            f"/api/v1/tickets/{ticket_id}/comments/",
            {"body": "Supplies confirmed.", "is_internal": True},
            format="json",
        )
        self.assertEqual(comment_response.status_code, 201)

        transition_response = self.client.post(
            f"/api/v1/tickets/{ticket_id}/transition/",
            {"status": "in_progress", "note": "Work started."},
            format="json",
        )
        self.assertEqual(transition_response.status_code, 200)

        complete_response = self.client.post(
            f"/api/v1/tickets/{ticket_id}/complete/",
            {
                "completion_summary": "Room and supplies are ready.",
                "time_spent_minutes": 30,
                "request_approval": True,
            },
            format="json",
        )
        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.data["status"], "waiting_approval")
        approval = TicketApproval.objects.get(ticket_id=ticket_id)

        approval_response = self.client.post(
            f"/api/v1/tickets/{ticket_id}/approvals/{approval.id}/review/",
            {"status": "approved", "decision_note": "Ready to close."},
            format="json",
        )
        self.assertEqual(approval_response.status_code, 200)

        ticket = Ticket.objects.get(id=ticket_id)
        self.assertEqual(ticket.status, Ticket.Status.COMPLETED)
        self.assertEqual(ticket.assigned_to, self.assignee)
        self.assertTrue(TicketComment.objects.filter(ticket=ticket, body="Supplies confirmed.").exists())
        self.assertTrue(AuditEvent.objects.filter(action="ticket.complete", target_id=str(ticket.id)).exists())
        self.assertTrue(AuditEvent.objects.filter(action="ticket.approval.review", target_id=str(ticket.id)).exists())

    def test_non_privileged_user_only_sees_own_or_assigned_tickets(self):
        own_ticket = Ticket.objects.create(
            ticket_number="HD-OWN",
            title="My assigned ticket",
            branch=self.branch,
            created_by=self.manager,
            assigned_to=self.assignee,
        )
        Ticket.objects.create(
            ticket_number="HD-OTHER",
            title="Other branch ticket",
            branch=self.other_branch,
            created_by=self.out_of_branch_user,
        )

        self.client.force_authenticate(user=self.assignee)
        response = self.client.get("/api/v1/tickets/")

        self.assertEqual(response.status_code, 200)
        ticket_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ticket_ids, {own_ticket.id})

    def test_summary_and_mobile_assigned_filter(self):
        assigned = Ticket.objects.create(
            ticket_number="HD-ME",
            title="Assigned mobile task",
            status=Ticket.Status.OPEN,
            priority=Ticket.Priority.URGENT,
            branch=self.branch,
            created_by=self.manager,
            assigned_to=self.assignee,
        )
        Ticket.objects.create(
            ticket_number="HD-NOT-ME",
            title="Unassigned task",
            status=Ticket.Status.OPEN,
            branch=self.branch,
            created_by=self.manager,
        )

        self.client.force_authenticate(user=self.assignee)
        list_response = self.client.get("/api/v1/tickets/", {"assigned_to": "me"})
        summary_response = self.client.get("/api/v1/tickets/summary/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual([item["id"] for item in list_response.data["results"]], [assigned.id])
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.data["assigned_to_me"], 1)
        self.assertEqual(summary_response.data["urgent"], 1)
