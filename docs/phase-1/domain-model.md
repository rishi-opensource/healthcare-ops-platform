# Domain Model

## Django App Boundaries

| App | Owns | Notes |
|-----|------|-------|
| `accounts` | users, roles, role assignments, auth profile, MFA flags | Custom user model from first migration |
| `core` | organizations, branches, locations, shared enums, soft-delete/archive helpers | Shared primitives only |
| `audit` | audit events, request metadata, immutable action log | Append-only service used by every app |
| `entities` | entity registry and typed profiles | Human and non-human business actors |
| `tickets` | tickets, status history, comments, attachments, approvals, task completions | Product backbone |
| `documents` | document templates, document files, contract assignments, acknowledgements, consent records | Stores metadata; files go to object storage |
| `training` | modules, assignments, quiz result placeholder, certificates, expiry | Compliance linked to users/entities |
| `scheduling` | roster, shifts, availability, leave, attendance, handover | Feeds payroll readiness |
| `payroll` | timesheet summaries, payroll readiness records, exceptions, exports | No payment execution in MVP |
| `inventory` | inventory items, batches, stock levels, stock movements, suppliers, purchase orders, deliveries, assets | Barcode-enabled workflows |
| `incidents` | incidents, escalations, emergency records, privacy breaches | Ticket-linked risk workflows |
| `communications` | patient/staff/supplier communication logs, notification intents | Provider abstraction later |
| `ai` | AI agents, AI action logs, draft actions, review queue | Human-review required |
| `reports` | report definitions, export jobs, cached aggregates | Uses data from other apps |

## Core Entities

### User

Represents a human account that can authenticate.

Key fields:
- `id`
- `email`
- `full_name`
- `phone`
- `is_active`
- `primary_branch`
- `created_at`
- `updated_at`

Relationships:
- many role assignments
- optional entity profile
- tickets created/assigned/completed
- audit events as actor

### Role and RoleAssignment

Represents domain authorization, not just Django groups.

Key fields:
- `role.code`
- `role.name`
- `role.description`
- `assignment.user`
- `assignment.role`
- `assignment.branch`
- `assignment.starts_at`
- `assignment.ends_at`

### Entity

Unified registry for people, organizations, assets, inventory, AI agents, rooms, branches, contracts, and services.

Key fields:
- `id`
- `entity_type`
- `display_name`
- `status`
- `branch`
- `owner_user`
- `responsible_user`
- `external_reference`
- `qr_code_value`
- `created_at`
- `updated_at`

Typed profiles:
- `StaffProfile`
- `SupplierProfile`
- `ContractorProfile`
- `PatientReferenceProfile`
- `AssetProfile`
- `InventoryItemProfile`
- `AIAgentProfile`
- `RoomProfile`
- `ServiceProfile`

### Ticket

Universal operational work record.

Key fields:
- `id`
- `ticket_number`
- `category`
- `title`
- `description`
- `status`
- `priority`
- `due_at`
- `branch`
- `created_by`
- `assigned_to`
- `related_entity`
- `source`
- `completion_summary`
- `completed_at`
- `created_at`
- `updated_at`

Related models:
- `TicketStatusHistory`
- `TicketComment`
- `TicketAttachment`
- `TicketApproval`
- `TaskCompletion`
- `TicketLink`

### Approval

Reusable approval record for tickets, payroll readiness, leave, contracts, incidents, and inventory.

Key fields:
- `id`
- `approval_type`
- `target_type`
- `target_id`
- `status`
- `requested_by`
- `reviewed_by`
- `reviewed_at`
- `decision_note`

### AuditEvent

Immutable operational trace.

Key fields:
- `id`
- `occurred_at`
- `actor_user`
- `actor_entity`
- `action`
- `target_type`
- `target_id`
- `branch`
- `request_id`
- `ip_address`
- `user_agent`
- `metadata`

No update/delete APIs should exist for audit events.

## Supporting Models by Module

### Documents

- `DocumentTemplate`
- `DocumentVersion`
- `DocumentFile`
- `DocumentAssignment`
- `ContractAssignment`
- `PolicyAcknowledgement`
- `ConsentRecord`

### Training

- `TrainingModule`
- `TrainingAssignment`
- `TrainingCompletion`
- `TrainingCertificate`

### Scheduling and Payroll

- `Roster`
- `Shift`
- `Availability`
- `LeaveRequest`
- `AttendanceEvent`
- `ShiftHandover`
- `TimesheetSummary`
- `PayrollReadinessRecord`
- `PayrollException`
- `PayrollExport`

### Inventory and Procurement

- `InventoryItem`
- `InventoryBatch`
- `StockLevel`
- `StockMovement`
- `Supplier`
- `PurchaseOrder`
- `Delivery`
- `Asset`
- `MaintenanceRecord`
- `BarcodeAlias`

### Incidents and Communications

- `Incident`
- `IncidentFollowUp`
- `EmergencyEvent`
- `PrivacyBreachRecord`
- `CommunicationLog`
- `NotificationIntent`

### AI

- `AIAgent`
- `AIActionLog`
- `AIDraftAction`
- `AIReview`

## Cross-Cutting Rules

- Most business models include `branch`, `created_by`, `created_at`, `updated_at`, and `status`.
- Sensitive models include explicit audit calls in service-layer methods.
- Business mutations should go through service functions, not direct serializer `save()` logic when workflow rules are involved.
- File uploads store metadata in Postgres and binary content in object storage.
- OpenAPI DTOs should avoid leaking internal model fields.

## Phase 2 Migration Order

1. `accounts` custom user and roles.
2. `core` organization/branch/location.
3. `audit` immutable event table.
4. `entities` base entity registry.
5. `tickets` base ticket tables.
6. `documents` base document metadata.

Later phases add feature-specific tables.
