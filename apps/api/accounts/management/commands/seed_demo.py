from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, RoleAssignment
from core.models import Branch, Organization
from documents.models import ConsentRecord, DocumentAssignment, DocumentTemplate, TrainingAssignment, TrainingModule
from entities.models import Entity, OnboardingStepTemplate, OnboardingWorkflowTemplate
from entities.services import create_entity_with_profile, start_entity_onboarding
from inventory.models import BarcodeAlias, InventoryBatch, PurchaseOrder, PurchaseOrderLine, StockItem
from inventory.services import receive_delivery, refresh_stock_status
from tickets.models import Ticket
from tickets.services import appraise_task_completion, approve_payroll_link, complete_ticket, create_ticket
from workforce.models import AttendanceRecord, HandoverNote, LeaveRequest, Shift, TimesheetSummary
from workforce.services import refresh_timesheet_summary


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
        if not Ticket.objects.filter(title="Complete morning reception checklist").exists():
            checklist_ticket = create_ticket(
                actor_user=manager,
                title="Complete morning reception checklist",
                description="Open reception, confirm appointment queue, and complete phone handover.",
                category=Ticket.Category.GENERAL,
                priority=Ticket.Priority.NORMAL,
                branch=branch,
                assigned_to=receptionist,
                source=Ticket.Source.SYSTEM,
            )
            complete_ticket(
                ticket=checklist_ticket,
                actor_user=receptionist,
                completion_summary="Reception opened and appointment queue checked.",
                task_name="Morning reception checklist",
                task_category="daily_workspace",
                time_spent_minutes=25,
                outcome="Ready for clinic start.",
                request_approval=False,
            )
            appraise_task_completion(
                ticket=checklist_ticket,
                actor_user=manager,
                appraisal_rating=5,
                appraisal_comments="Completed accurately before clinic opening.",
            )
            approve_payroll_link(
                ticket=checklist_ticket,
                actor_user=manager,
                approved=True,
                note="Approved for payroll readiness report.",
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
        employment_template, _ = DocumentTemplate.objects.get_or_create(
            name="Employment Agreement",
            defaults={
                "template_type": DocumentTemplate.TemplateType.EMPLOYMENT_AGREEMENT,
                "description": "Standard employment agreement for clinic staff.",
                "current_version": "1.0",
            },
        )
        ai_usage_template, _ = DocumentTemplate.objects.get_or_create(
            name="AI Usage and Voice Assistant Policy",
            defaults={
                "template_type": DocumentTemplate.TemplateType.AI_USAGE,
                "description": "Acknowledgement for safe AI and voice assistant usage.",
                "current_version": "1.0",
            },
        )
        privacy_training, _ = TrainingModule.objects.get_or_create(
            title="Privacy and Patient Confidentiality",
            defaults={
                "module_type": TrainingModule.ModuleType.PRIVACY,
                "description": "Mandatory privacy, confidentiality, and patient information handling training.",
                "quiz_required": True,
                "validity_days": 365,
            },
        )
        emergency_training, _ = TrainingModule.objects.get_or_create(
            title="Emergency Response and Incident Reporting",
            defaults={
                "module_type": TrainingModule.ModuleType.EMERGENCY,
                "description": "Clinic emergency workflow, panic escalation, and incident reporting training.",
                "quiz_required": True,
                "validity_days": 365,
            },
        )
        ai_training, _ = TrainingModule.objects.get_or_create(
            title="AI Governance for Staff",
            defaults={
                "module_type": TrainingModule.ModuleType.AI_GOVERNANCE,
                "description": "Human review, voice command safety, and AI action audit expectations.",
                "quiz_required": False,
                "validity_days": 365,
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
        else:
            staff_entity = Entity.objects.get(display_name="Reception Coordinator")
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
        else:
            supplier_entity = Entity.objects.get(display_name="ABC Medical Supplies")
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

        due_soon = timezone.now() + timedelta(days=14)
        expires_later = timezone.now() + timedelta(days=365)
        for template in [employment_template, privacy_template, ai_usage_template]:
            DocumentAssignment.objects.get_or_create(
                template=template,
                assigned_to_user=receptionist,
                assigned_to_entity=staff_entity,
                defaults={
                    "assigned_by": user,
                    "due_at": due_soon,
                    "expires_at": expires_later,
                    "version": template.current_version,
                    "metadata": {"source": "seed_demo"},
                },
            )
        DocumentAssignment.objects.get_or_create(
            template=supplier_template,
            assigned_to_entity=supplier_entity,
            defaults={
                "assigned_by": user,
                "due_at": due_soon,
                "expires_at": expires_later,
                "version": supplier_template.current_version,
                "metadata": {"source": "seed_demo"},
            },
        )
        ConsentRecord.objects.get_or_create(
            consent_type=ConsentRecord.ConsentType.AI_USAGE,
            subject_user=receptionist,
            subject_entity=staff_entity,
            purpose="Use mobile voice assistant for operational tasks",
            defaults={
                "status": ConsentRecord.Status.GIVEN,
                "scope": "Operational commands, ticket creation, scanning support, and task search.",
                "granted_by": user,
                "granted_at": timezone.now(),
                "expires_at": expires_later,
                "metadata": {"source": "seed_demo"},
            },
        )
        for module in [privacy_training, emergency_training, ai_training]:
            TrainingAssignment.objects.get_or_create(
                module=module,
                assigned_to_user=receptionist,
                assigned_to_entity=staff_entity,
                defaults={
                    "assigned_by": manager,
                    "due_at": due_soon,
                    "metadata": {"source": "seed_demo"},
                },
            )

        shift_start = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        shift_end = shift_start + timedelta(hours=8)
        shift, _ = Shift.objects.get_or_create(
            staff_user=receptionist,
            starts_at=shift_start,
            defaults={
                "branch": branch,
                "role_label": "Reception",
                "ends_at": shift_end,
                "status": Shift.Status.PUBLISHED,
                "notes": "Front desk and patient arrival support.",
                "published_by": manager,
                "published_at": timezone.now(),
            },
        )
        LeaveRequest.objects.get_or_create(
            staff_user=receptionist,
            starts_at=timezone.now() + timedelta(days=21),
            defaults={
                "branch": branch,
                "leave_type": LeaveRequest.LeaveType.ANNUAL,
                "ends_at": timezone.now() + timedelta(days=22),
                "reason": "Family appointment.",
            },
        )
        clock_in_at = timezone.now().replace(hour=8, minute=55, second=0, microsecond=0)
        AttendanceRecord.objects.get_or_create(
            staff_user=receptionist,
            clock_in_at=clock_in_at,
            defaults={
                "shift": shift,
                "branch": branch,
                "clock_out_at": clock_in_at + timedelta(hours=8),
                "status": AttendanceRecord.Status.CLOCKED_OUT,
                "location_label": "Main Clinic",
                "approved_by": manager,
                "approved_at": timezone.now(),
            },
        )
        HandoverNote.objects.get_or_create(
            branch=branch,
            title="Follow up pathology phone message",
            defaults={
                "author": manager,
                "assigned_to": receptionist,
                "body": "Call patient back after confirming the doctor has reviewed the message.",
                "due_at": timezone.now() + timedelta(days=1),
            },
        )
        today = timezone.now().date()
        period_start = today - timedelta(days=today.weekday())
        period_end = today
        summary = refresh_timesheet_summary(
            staff_user=receptionist,
            period_start=period_start,
            period_end=period_end,
            actor_user=user,
        )
        if summary.status == TimesheetSummary.Status.DRAFT:
            summary.status = TimesheetSummary.Status.SUBMITTED
            summary.submitted_at = timezone.now()
            summary.save(update_fields=["status", "submitted_at", "updated_at"])

        inventory_item = Entity.objects.get(display_name="Nitrile Gloves Medium")
        stock_item, _ = StockItem.objects.get_or_create(
            branch=branch,
            sku="GLOVE-M",
            defaults={
                "entity": inventory_item,
                "name": "Nitrile Gloves Medium",
                "barcode": "093000000001",
                "unit": "box",
                "quantity_on_hand": 10,
                "reorder_threshold": 12,
                "preferred_supplier": supplier_entity,
            },
        )
        refresh_stock_status(stock_item)
        batch, _ = InventoryBatch.objects.get_or_create(
            stock_item=stock_item,
            batch_number="GLV-2026-01",
            defaults={
                "expiry_date": timezone.now().date() + timedelta(days=25),
                "quantity": stock_item.quantity_on_hand,
                "location_label": "Treatment room shelf A",
            },
        )
        BarcodeAlias.objects.get_or_create(
            barcode="093000000001",
            defaults={
                "target_type": BarcodeAlias.TargetType.STOCK_ITEM,
                "stock_item": stock_item,
                "label": stock_item.name,
            },
        )
        purchase_order, _ = PurchaseOrder.objects.get_or_create(
            branch=branch,
            supplier=supplier_entity,
            po_number="PO-000001",
            defaults={
                "requested_by": manager,
                "expected_at": timezone.now() + timedelta(days=7),
                "notes": "Reorder gloves for treatment room.",
            },
        )
        PurchaseOrderLine.objects.get_or_create(
            purchase_order=purchase_order,
            stock_item=stock_item,
            defaults={"quantity_ordered": 20},
        )
        if not stock_item.deliveries.exists():
            receive_delivery(
                stock_item=stock_item,
                purchase_order=purchase_order,
                actor_user=manager,
                quantity_received=5,
                batch_number=batch.batch_number,
                expiry_date=batch.expiry_date,
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo data. Login: admin@healthcare.local / ChangeMe123!"))
