from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role, RoleAssignment
from core.models import Branch, Organization
from documents.models import DocumentTemplate
from entities.models import Entity, OnboardingStepTemplate, OnboardingWorkflowTemplate
from entities.services import create_entity_with_profile, start_entity_onboarding
from tickets.models import Ticket
from tickets.services import create_ticket


class Command(BaseCommand):
    help = "Seed Phase 2 demo organization, branch, roles, and a super admin."

    def handle(self, *args, **options):
        organization, _ = Organization.objects.get_or_create(
            name="Healthcare Doctors",
            defaults={
                "legal_name": "Thoshi Medicals Pty Ltd",
                "trading_name": "Healthcare Doctors",
            },
        )
        branch, _ = Branch.objects.get_or_create(
            organization=organization,
            code="main",
            defaults={"name": "Main Clinic"},
        )

        for code, label in Role.Codes.choices:
            Role.objects.get_or_create(code=code, defaults={"name": label})

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email="admin@healthcare.local",
            defaults={
                "full_name": "Healthcare Super Admin",
                "is_staff": True,
                "is_superuser": True,
                "primary_branch": branch,
            },
        )
        if created:
            user.set_password("ChangeMe123!")
            user.save()

        super_admin_role = Role.objects.get(code=Role.Codes.SUPER_ADMIN)
        RoleAssignment.objects.get_or_create(user=user, role=super_admin_role, branch=None)

        manager_role = Role.objects.get(code=Role.Codes.MANAGER)
        receptionist_role = Role.objects.get(code=Role.Codes.RECEPTIONIST)
        manager, manager_created = User.objects.get_or_create(
            email="manager@healthcare.local",
            defaults={
                "full_name": "Main Clinic Manager",
                "primary_branch": branch,
            },
        )
        if manager_created:
            manager.set_password("ChangeMe123!")
            manager.save()
        receptionist, receptionist_created = User.objects.get_or_create(
            email="reception@healthcare.local",
            defaults={
                "full_name": "Reception Coordinator",
                "primary_branch": branch,
            },
        )
        if receptionist_created:
            receptionist.set_password("ChangeMe123!")
            receptionist.save()
        RoleAssignment.objects.get_or_create(user=manager, role=manager_role, branch=branch)
        RoleAssignment.objects.get_or_create(user=receptionist, role=receptionist_role, branch=branch)

        if not Ticket.objects.filter(title="Prepare flu clinic room").exists():
            create_ticket(
                actor_user=manager,
                title="Prepare flu clinic room",
                description="Confirm room setup, signage, vaccine fridge check, and reception script.",
                category=Ticket.Category.APPOINTMENT,
                priority=Ticket.Priority.HIGH,
                branch=branch,
                assigned_to=receptionist,
                source=Ticket.Source.SYSTEM,
            )
        if not Ticket.objects.filter(title="Review expiring first aid stock").exists():
            create_ticket(
                actor_user=user,
                title="Review expiring first aid stock",
                description="Check treatment room batch dates and raise reorder items.",
                category=Ticket.Category.INVENTORY,
                priority=Ticket.Priority.URGENT,
                branch=branch,
                assigned_to=manager,
                source=Ticket.Source.SYSTEM,
            )

        privacy_template, _ = DocumentTemplate.objects.get_or_create(
            name="Privacy and Confidentiality Acknowledgement",
            defaults={
                "template_type": DocumentTemplate.TemplateType.PRIVACY_ACKNOWLEDGEMENT,
                "description": "Required privacy and confidentiality acknowledgement for onboarding.",
            },
        )
        supplier_template, _ = DocumentTemplate.objects.get_or_create(
            name="Supplier Compliance Pack",
            defaults={
                "template_type": DocumentTemplate.TemplateType.SUPPLIER_AGREEMENT,
                "description": "Supplier compliance onboarding pack.",
            },
        )
        staff_workflow, _ = OnboardingWorkflowTemplate.objects.get_or_create(
            entity_type=Entity.Types.EMPLOYEE,
            name="Staff onboarding",
            defaults={"description": "Staff onboarding workflow for clinic employees."},
        )
        supplier_workflow, _ = OnboardingWorkflowTemplate.objects.get_or_create(
            entity_type=Entity.Types.SUPPLIER,
            name="Supplier onboarding",
            defaults={"description": "Supplier onboarding workflow with compliance review."},
        )
        inventory_workflow, _ = OnboardingWorkflowTemplate.objects.get_or_create(
            entity_type=Entity.Types.INVENTORY_ITEM,
            name="Inventory item onboarding",
            defaults={"description": "Inventory item registration, barcode, and stocking checks."},
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=staff_workflow,
            order=1,
            defaults={
                "name": "Verify staff profile",
                "step_type": OnboardingStepTemplate.StepType.PROFILE,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=staff_workflow,
            order=2,
            defaults={
                "name": "Privacy acknowledgement",
                "step_type": OnboardingStepTemplate.StepType.DOCUMENT,
                "document_template": privacy_template,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=staff_workflow,
            order=3,
            defaults={
                "name": "Manager activation review",
                "step_type": OnboardingStepTemplate.StepType.APPROVAL,
                "ticket_category": Ticket.Category.ONBOARDING,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=supplier_workflow,
            order=1,
            defaults={
                "name": "Supplier compliance document",
                "step_type": OnboardingStepTemplate.StepType.DOCUMENT,
                "document_template": supplier_template,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=supplier_workflow,
            order=2,
            defaults={
                "name": "Compliance approval",
                "step_type": OnboardingStepTemplate.StepType.APPROVAL,
                "ticket_category": Ticket.Category.SUPPLIER,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=inventory_workflow,
            order=1,
            defaults={
                "name": "Assign barcode",
                "step_type": OnboardingStepTemplate.StepType.QR_BARCODE,
                "ticket_category": Ticket.Category.INVENTORY,
            },
        )
        OnboardingStepTemplate.objects.get_or_create(
            workflow_template=inventory_workflow,
            order=2,
            defaults={
                "name": "Verify reorder threshold",
                "step_type": OnboardingStepTemplate.StepType.REVIEW,
            },
        )

        if not Entity.objects.filter(display_name="Reception Coordinator").exists():
            staff_entity = create_entity_with_profile(
                actor_user=user,
                entity_type=Entity.Types.EMPLOYEE,
                display_name="Reception Coordinator",
                status=Entity.Status.DRAFT,
                branch=branch,
                owner_user=receptionist,
                responsible_user=manager,
                external_reference="STAFF-REC-001",
                profile={"user": receptionist, "employment_type": "full_time"},
            )
            start_entity_onboarding(entity=staff_entity, actor_user=user)
        if not Entity.objects.filter(display_name="ABC Medical Supplies").exists():
            supplier_entity = create_entity_with_profile(
                actor_user=user,
                entity_type=Entity.Types.SUPPLIER,
                display_name="ABC Medical Supplies",
                status=Entity.Status.DRAFT,
                branch=branch,
                responsible_user=manager,
                external_reference="SUP-ABC-001",
                profile={"supplier_code": "ABC-MED"},
            )
            start_entity_onboarding(entity=supplier_entity, actor_user=user)
        if not Entity.objects.filter(display_name="Nitrile Gloves Medium").exists():
            inventory_entity = create_entity_with_profile(
                actor_user=manager,
                entity_type=Entity.Types.INVENTORY_ITEM,
                display_name="Nitrile Gloves Medium",
                status=Entity.Status.DRAFT,
                branch=branch,
                responsible_user=manager,
                external_reference="SKU-GLOVE-M",
                profile={"sku": "GLOVE-M", "barcode": "093000000001", "unit": "box", "reorder_threshold": 12},
            )
            start_entity_onboarding(entity=inventory_entity, actor_user=manager)

        self.stdout.write(self.style.SUCCESS("Seeded demo data. Login: admin@healthcare.local / ChangeMe123!"))
