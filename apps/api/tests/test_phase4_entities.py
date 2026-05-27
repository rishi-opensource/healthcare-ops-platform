from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from documents.models import DocumentAssignment, DocumentTemplate
from entities.models import (
    Entity,
    EntityOnboarding,
    OnboardingStepCompletion,
    OnboardingStepTemplate,
    OnboardingWorkflowTemplate,
)


class Phase4EntityOnboardingTests(TestCase):
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
        self.receptionist = User.objects.create_user(
            email="reception@example.com",
            password="ChangeMe123!",
            full_name="Reception User",
            primary_branch=self.branch,
        )
        self.north_user = User.objects.create_user(
            email="north@example.com",
            password="ChangeMe123!",
            full_name="North User",
            primary_branch=self.other_branch,
        )
        RoleAssignment.objects.create(user=self.manager, role=manager_role, branch=self.branch)
        RoleAssignment.objects.create(user=self.receptionist, role=receptionist_role, branch=self.branch)
        self.template = DocumentTemplate.objects.create(
            name="Privacy Acknowledgement",
            template_type=DocumentTemplate.TemplateType.PRIVACY_ACKNOWLEDGEMENT,
        )
        self.workflow = OnboardingWorkflowTemplate.objects.create(
            entity_type=Entity.Types.EMPLOYEE,
            name="Staff onboarding",
        )
        OnboardingStepTemplate.objects.create(
            workflow_template=self.workflow,
            name="Verify staff profile",
            step_type=OnboardingStepTemplate.StepType.PROFILE,
            order=1,
        )
        OnboardingStepTemplate.objects.create(
            workflow_template=self.workflow,
            name="Privacy acknowledgement",
            step_type=OnboardingStepTemplate.StepType.DOCUMENT,
            order=2,
            document_template=self.template,
        )
        OnboardingStepTemplate.objects.create(
            workflow_template=self.workflow,
            name="Manager activation review",
            step_type=OnboardingStepTemplate.StepType.APPROVAL,
            order=3,
            ticket_category="onboarding",
        )
        self.client = APIClient()

    def test_create_entity_starts_onboarding_and_activation_flow(self):
        self.client.force_authenticate(user=self.manager)
        create_response = self.client.post(
            "/api/v1/entities/",
            {
                "entity_type": "employee",
                "display_name": "New Receptionist",
                "status": "draft",
                "branch": self.branch.id,
                "owner_user": self.receptionist.id,
                "responsible_user": self.manager.id,
                "external_reference": "STAFF-NEW-001",
                "profile": {"user": self.receptionist.id, "employment_type": "part_time"},
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        entity_id = create_response.data["id"]
        entity = Entity.objects.get(id=entity_id)
        self.assertTrue(entity.qr_code_value.startswith("HD-ENTITY-"))

        start_response = self.client.post(f"/api/v1/entities/{entity_id}/start-onboarding/", {}, format="json")
        self.assertEqual(start_response.status_code, 200)
        self.assertEqual(start_response.data["status"], EntityOnboarding.Status.IN_PROGRESS)
        self.assertEqual(len(start_response.data["step_completions"]), 3)
        self.assertTrue(DocumentAssignment.objects.filter(assigned_to_entity=entity).exists())

        activate_too_early = self.client.post(
            f"/api/v1/entities/{entity_id}/activate/",
            {"status": "active", "note": "Activate"},
            format="json",
        )
        self.assertEqual(activate_too_early.status_code, 400)

        for step in OnboardingStepCompletion.objects.filter(onboarding__entity=entity):
            complete_response = self.client.post(
                f"/api/v1/entities/{entity_id}/complete-onboarding-step/",
                {"step_completion": step.id, "status": "completed", "note": "Done"},
                format="json",
            )
            self.assertEqual(complete_response.status_code, 200)

        activate_response = self.client.post(
            f"/api/v1/entities/{entity_id}/activate/",
            {"status": "active", "note": "Approved"},
            format="json",
        )
        self.assertEqual(activate_response.status_code, 200)
        entity.refresh_from_db()
        self.assertEqual(entity.status, Entity.Status.ACTIVE)
        self.assertTrue(AuditEvent.objects.filter(action="entity.onboarding.start", target_id=str(entity.id)).exists())
        self.assertTrue(AuditEvent.objects.filter(action="entity.status.transition", target_id=str(entity.id)).exists())

    def test_entity_permissions_are_branch_and_assignment_scoped(self):
        visible = Entity.objects.create(
            entity_type=Entity.Types.EMPLOYEE,
            display_name="Visible Entity",
            status=Entity.Status.ONBOARDING,
            branch=self.branch,
            responsible_user=self.receptionist,
        )
        Entity.objects.create(
            entity_type=Entity.Types.EMPLOYEE,
            display_name="Hidden Entity",
            status=Entity.Status.ONBOARDING,
            branch=self.other_branch,
            responsible_user=self.north_user,
        )

        self.client.force_authenticate(user=self.receptionist)
        response = self.client.get("/api/v1/entities/")

        self.assertEqual(response.status_code, 200)
        entity_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(entity_ids, {visible.id})

    def test_onboarding_summary_counts_pending_steps(self):
        entity = Entity.objects.create(
            entity_type=Entity.Types.EMPLOYEE,
            display_name="Summary Entity",
            status=Entity.Status.ONBOARDING,
            branch=self.branch,
            responsible_user=self.manager,
        )
        onboarding = EntityOnboarding.objects.create(
            entity=entity,
            workflow_template=self.workflow,
            status=EntityOnboarding.Status.IN_PROGRESS,
            started_by=self.manager,
        )
        OnboardingStepCompletion.objects.create(
            onboarding=onboarding,
            name="Pending step",
            step_type=OnboardingStepTemplate.StepType.PROFILE,
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get("/api/v1/entities/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["onboarding"], 1)
        self.assertEqual(response.data["pending_steps"], 1)
