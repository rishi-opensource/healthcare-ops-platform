from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from tickets.models import Ticket


class Phase2FoundationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Healthcare Doctors")
        self.branch = Branch.objects.create(
            organization=self.organization,
            name="Main Clinic",
            code="main",
        )
        self.role = Role.objects.create(code=Role.Codes.SUPER_ADMIN, name="Super Admin")
        User = get_user_model()
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="ChangeMe123!",
            full_name="Admin User",
            primary_branch=self.branch,
            is_staff=True,
            is_superuser=True,
        )
        RoleAssignment.objects.create(user=self.user, role=self.role)
        self.client = APIClient()

    def test_health_endpoint_is_public(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")

    def test_login_returns_token_and_audits(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "admin@example.com", "password": "ChangeMe123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], "admin@example.com")
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        self.assertTrue(AuditEvent.objects.filter(action="auth.login", actor_user=self.user).exists())

    def test_authenticated_user_can_create_ticket(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/v1/tickets/",
            {
                "title": "Check vaccine fridge",
                "description": "Temperature check and log.",
                "category": "inventory",
                "priority": "high",
                "branch": self.branch.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        ticket = Ticket.objects.get()
        self.assertTrue(ticket.ticket_number.startswith("HD-"))
        self.assertEqual(ticket.created_by, self.user)
        self.assertTrue(AuditEvent.objects.filter(action="ticket.create", target_id=str(ticket.id)).exists())

