from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from tickets.models import Ticket
from tickets.services import complete_ticket, create_ticket
from workforce.models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary


class Phase7WorkforceTests(TestCase):
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
        self.shift = Shift.objects.create(
            branch=self.branch,
            staff_user=self.receptionist,
            role_label="Reception",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=8),
        )
        self.client = APIClient()

    def test_shift_publish_and_leave_review_are_audited(self):
        self.client.force_authenticate(user=self.manager)
        leave = LeaveRequest.objects.create(
            staff_user=self.receptionist,
            branch=self.branch,
            starts_at=timezone.now() + timedelta(days=7),
            ends_at=timezone.now() + timedelta(days=8),
            reason="Appointment.",
        )

        shift_response = self.client.post(f"/api/v1/shifts/{self.shift.id}/publish/", {}, format="json")
        leave_response = self.client.post(
            f"/api/v1/leave-requests/{leave.id}/review/",
            {"status": LeaveRequest.Status.APPROVED, "note": "Coverage confirmed."},
            format="json",
        )

        self.assertEqual(shift_response.status_code, 200)
        self.assertEqual(shift_response.data["status"], Shift.Status.PUBLISHED)
        self.assertEqual(leave_response.status_code, 200)
        self.assertEqual(leave_response.data["status"], LeaveRequest.Status.APPROVED)
        self.assertTrue(AuditEvent.objects.filter(action="workforce.shift.publish").exists())
        self.assertTrue(AuditEvent.objects.filter(action="workforce.leave.review").exists())

    def test_clock_in_clock_out_and_handover_acknowledgement(self):
        self.client.force_authenticate(user=self.receptionist)
        handover = HandoverNote.objects.create(
            branch=self.branch,
            author=self.manager,
            assigned_to=self.receptionist,
            title="Call patient",
            body="Follow up appointment question.",
        )

        clock_in = self.client.post("/api/v1/attendance-records/clock-in/", {"shift": self.shift.id}, format="json")
        clock_out = self.client.post(
            f"/api/v1/attendance-records/{clock_in.data['id']}/clock-out/",
            {"exception_note": "Forgot to clock out on time."},
            format="json",
        )
        acknowledge = self.client.post(f"/api/v1/handover-notes/{handover.id}/acknowledge/", {}, format="json")

        self.assertEqual(clock_in.status_code, 200)
        self.assertEqual(clock_in.data["status"], AttendanceRecord.Status.CLOCKED_IN)
        self.assertEqual(clock_out.status_code, 200)
        self.assertEqual(clock_out.data["status"], AttendanceRecord.Status.EXCEPTION)
        self.assertEqual(acknowledge.status_code, 200)
        self.assertEqual(acknowledge.data["status"], HandoverNote.Status.ACKNOWLEDGED)

    def test_timesheet_refresh_submit_review_and_summary(self):
        self.client.force_authenticate(user=self.receptionist)
        attendance = AttendanceRecord.objects.create(
            staff_user=self.receptionist,
            shift=self.shift,
            branch=self.branch,
            clock_in_at=timezone.now() - timedelta(hours=8),
            clock_out_at=timezone.now(),
            status=AttendanceRecord.Status.CLOCKED_OUT,
        )
        ticket = create_ticket(
            actor_user=self.manager,
            title="Reception task",
            description="Daily task.",
            category=Ticket.Category.GENERAL,
            branch=self.branch,
            assigned_to=self.receptionist,
        )
        complete_ticket(
            ticket=ticket,
            actor_user=self.receptionist,
            completion_summary="Done.",
            time_spent_minutes=30,
            request_approval=False,
        )

        refresh = self.client.post("/api/v1/timesheet-summaries/refresh/", {}, format="json")
        submit = self.client.post(f"/api/v1/timesheet-summaries/{refresh.data['id']}/submit/", {}, format="json")
        self.client.force_authenticate(user=self.manager)
        review = self.client.post(
            f"/api/v1/timesheet-summaries/{refresh.data['id']}/review/",
            {"status": TimesheetSummary.Status.APPROVED, "note": "Ready for payroll."},
            format="json",
        )
        summary = self.client.get("/api/v1/timesheet-summaries/summary/")

        self.assertEqual(refresh.status_code, 200)
        self.assertEqual(refresh.data["worked_minutes"], 480)
        self.assertEqual(refresh.data["task_minutes"], 30)
        self.assertEqual(submit.status_code, 200)
        self.assertEqual(submit.data["status"], TimesheetSummary.Status.SUBMITTED)
        self.assertEqual(review.status_code, 200)
        self.assertTrue(review.data["payroll_ready"])
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data["payroll_ready"], 1)
        attendance.refresh_from_db()
