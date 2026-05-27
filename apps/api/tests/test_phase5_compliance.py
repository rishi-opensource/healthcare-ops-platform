from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from documents.models import ConsentRecord, DocumentAssignment, DocumentTemplate, TrainingAssignment, TrainingModule
from documents.tasks import refresh_compliance_expiry_statuses
from entities.models import Entity


class Phase5ComplianceTests(TestCase):
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
        self.entity = Entity.objects.create(
            entity_type=Entity.Types.EMPLOYEE,
            display_name="Reception User",
            status=Entity.Status.ACTIVE,
            branch=self.branch,
            owner_user=self.receptionist,
            responsible_user=self.manager,
        )
        self.template = DocumentTemplate.objects.create(
            name="Employment Agreement",
            template_type=DocumentTemplate.TemplateType.EMPLOYMENT_AGREEMENT,
            current_version="1.0",
        )
        self.assignment = DocumentAssignment.objects.create(
            template=self.template,
            assigned_to_user=self.receptionist,
            assigned_to_entity=self.entity,
            assigned_by=self.manager,
            due_at=timezone.now() + timedelta(days=7),
            expires_at=timezone.now() + timedelta(days=365),
        )
        self.module = TrainingModule.objects.create(
            title="Privacy and Patient Confidentiality",
            module_type=TrainingModule.ModuleType.PRIVACY,
            quiz_required=True,
            validity_days=365,
        )
        self.training = TrainingAssignment.objects.create(
            module=self.module,
            assigned_to_user=self.receptionist,
            assigned_to_entity=self.entity,
            assigned_by=self.manager,
            due_at=timezone.now() + timedelta(days=7),
        )
        self.consent = ConsentRecord.objects.create(
            consent_type=ConsentRecord.ConsentType.AI_USAGE,
            subject_user=self.receptionist,
            subject_entity=self.entity,
            status=ConsentRecord.Status.GIVEN,
            purpose="Use mobile voice assistant",
            scope="Operational tasks only.",
            granted_by=self.manager,
            granted_at=timezone.now(),
        )
        self.client = APIClient()

    def test_document_acknowledgement_and_signature_are_audited(self):
        self.client.force_authenticate(user=self.receptionist)

        acknowledge_response = self.client.post(
            f"/api/v1/document-assignments/{self.assignment.id}/acknowledge/",
            {"acknowledgement_text": "I acknowledge this policy.", "evidence_label": "Mobile acknowledgement"},
            format="json",
        )
        self.assertEqual(acknowledge_response.status_code, 200)
        self.assertEqual(acknowledge_response.data["status"], DocumentAssignment.Status.ACKNOWLEDGED)

        sign_response = self.client.post(
            f"/api/v1/document-assignments/{self.assignment.id}/sign/",
            {"acknowledgement_text": "Signed digitally.", "evidence_label": "Digital signature"},
            format="json",
        )
        self.assertEqual(sign_response.status_code, 200)
        self.assertEqual(sign_response.data["status"], DocumentAssignment.Status.SIGNED)
        self.assertTrue(
            AuditEvent.objects.filter(action="document.assignment.sign", target_id=str(self.assignment.id)).exists()
        )

    def test_training_completion_sets_certificate_expiry_and_summary(self):
        self.client.force_authenticate(user=self.receptionist)

        complete_response = self.client.post(
            f"/api/v1/training-assignments/{self.training.id}/complete/",
            {"completion_note": "Passed quiz.", "quiz_score": 94, "evidence_label": "Certificate"},
            format="json",
        )
        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.data["status"], TrainingAssignment.Status.COMPLETED)
        self.assertEqual(complete_response.data["quiz_score"], 94)
        self.assertTrue(complete_response.data["certificate_label"].startswith("CERT-"))
        self.assertIsNotNone(complete_response.data["expires_at"])

        summary_response = self.client.get("/api/v1/training-assignments/summary/")
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.data["assigned_training"], 1)
        self.assertEqual(summary_response.data["completed_training"], 1)
        self.assertTrue(
            AuditEvent.objects.filter(action="training.assignment.complete", target_id=str(self.training.id)).exists()
        )

    def test_consent_withdrawal_is_audited(self):
        self.client.force_authenticate(user=self.receptionist)

        response = self.client.post(f"/api/v1/consent-records/{self.consent.id}/withdraw/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], ConsentRecord.Status.WITHDRAWN)
        self.assertTrue(AuditEvent.objects.filter(action="consent.withdraw", target_id=str(self.consent.id)).exists())

    def test_compliance_expiry_task_marks_overdue_and_expired_records(self):
        self.assignment.due_at = timezone.now() - timedelta(days=1)
        self.assignment.save(update_fields=["due_at", "updated_at"])
        self.training.due_at = timezone.now() - timedelta(days=1)
        self.training.save(update_fields=["due_at", "updated_at"])
        self.consent.expires_at = timezone.now() - timedelta(days=1)
        self.consent.save(update_fields=["expires_at", "updated_at"])

        result = refresh_compliance_expiry_statuses.delay().get()

        self.assertEqual(result["expired_documents"], 1)
        self.assertEqual(result["overdue_training"], 1)
        self.assertEqual(result["expired_consents"], 1)
        self.assignment.refresh_from_db()
        self.training.refresh_from_db()
        self.consent.refresh_from_db()
        self.assertEqual(self.assignment.status, DocumentAssignment.Status.EXPIRED)
        self.assertEqual(self.training.status, TrainingAssignment.Status.OVERDUE)
        self.assertEqual(self.consent.status, ConsentRecord.Status.EXPIRED)
