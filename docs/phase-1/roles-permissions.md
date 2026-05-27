# Roles and Permissions

## Permission Principles

- Default deny for all authenticated API access.
- Super Admin has system-wide visibility but all actions remain audited.
- Managers can act only within assigned branch, team, or responsibility scope.
- Staff can view and update assigned work, their own roster/leave/training/contracts, and tickets they created or are assigned to.
- Sensitive actions require explicit permissions and approval records.
- AI agents cannot approve, delete, sign, close sensitive incidents, or alter payroll/payment state.
- Suppliers, contractors, and patients have restricted portal/API access only when those portals are explicitly enabled.

## Role Hierarchy

| Role | Primary scope | Default access |
|------|---------------|----------------|
| Super Admin | Entire platform | Full read, full admin actions, final approvals, reports, audit review |
| Clinic Manager / Practice Manager | Assigned clinic/branch/team | Operational tickets, roster, leave, incidents, staff performance, payroll readiness review |
| HR / Payroll Admin | Staff lifecycle and pay readiness | Onboarding, contracts, training, attendance, timesheets, payroll readiness exports |
| Finance / Accounts User | Financial controls | Payroll readiness reports, supplier/payment status, finance exports, purchase/order review |
| Compliance Officer | Compliance and risk | Audit trails, training, contracts, incidents, privacy, AI activity, policy acknowledgements |
| Receptionist | Daily operational work | Own dashboard, assigned tickets, roster, leave, scanning, handover, patient communication logs |
| Doctor / Practitioner | Clinical/administrative work | Assigned patient-related tasks, own documents/training, work summary, relevant communication |
| Nurse / Clinical Assistant | Clinical support work | Assigned tickets, treatment-room tasks, stock usage, incidents, equipment checks |
| Pharmacist / Medication Manager | Medication and controlled stock | Medication inventory, expiry, batches, controlled-item tracking, supplier issues |
| Inventory / Procurement User | Stock and assets | Inventory, deliveries, stock movement, reorder tickets, supplier issues, assets |
| Supplier / Vendor | External supplier records | Own profile, assigned purchase/delivery tickets, documents, invoices where enabled |
| Contractor / Service Provider | External work records | Own profile, assigned job tickets, evidence submission, payment-readiness status |
| AI Agent | System actor | Draft tickets/actions, summaries, recommendations, no sensitive final approvals |

## Permission Matrix

Legend: `R` read, `C` create, `U` update, `A` approve, `X` export, `-` no default access.

| Area | Super Admin | Manager | HR/Payroll | Finance | Compliance | Receptionist | Doctor | Nurse | Pharmacist | Inventory | Supplier | Contractor | AI Agent |
|------|-------------|---------|------------|---------|------------|--------------|--------|-------|------------|-----------|----------|------------|----------|
| Dashboard | R X | R | R | R | R | R own | R own | R own | R own | R | - | R own | - |
| Tickets | R C U A X | R C U A | R C U A | R | R | R C U | R C U | R C U | R C U | R C U | R U own | R U own | C draft |
| Entity registry | R C U X | R U scoped | R C U | R scoped | R | R limited | R limited | R limited | R limited | R C U inventory | R own | R own | R own |
| Onboarding | R C U A | R U A scoped | R C U A | R payment scoped | R | R own | R own | R own | R own | R inventory | R own | R own | C draft |
| Contracts/consent | R C U A X | R A scoped | R C U A | R scoped | R C U A | R own | R own | R own | R own | R scoped | R own | R own | C draft |
| Training | R C U A X | R A scoped | R C U A | R | R C U A | R U own | R U own | R U own | R U own | R U own | - | R U own | C draft |
| Roster/leave | R C U A X | R C U A | R C U A | R | R | R C own | R C own | R C own | R C own | R C own | - | R own | - |
| Attendance/timesheet | R U A X | R U A | R U A X | R X | R | R C own | R C own | R C own | R C own | R C own | - | R own | - |
| Payroll readiness | R A X | R A scoped | R U A X | R A X | R | R own | R own | R own | R own | R own | R own if enabled | R own | C draft |
| Inventory/barcode | R C U A X | R C U A | R | R | R | R C U scoped | R C scoped | R C U scoped | R C U A | R C U A | R own deliveries | R assigned | C draft |
| Incidents | R C U A X | R C U A | R scoped | R limited | R C U A X | R C U | R C U | R C U | R C U | R C U | C own issue | C own issue | C draft |
| Reports | R X | R X scoped | R X scoped | R X finance | R X compliance | R own | R own | R own | R own | R X inventory | - | R own | - |
| Audit logs | R X | R scoped | R scoped | R finance | R X compliance | R own | R own | R own | R own | R scoped | - | - | - |
| AI actions | R U A X | R U A scoped | R U A scoped | R scoped | R U A X | R C | R C | R C | R C | R C | - | - | C draft |

## Approval Defaults

| Approval type | Can approve by default | Cannot approve |
|---------------|------------------------|----------------|
| Ticket completion | Manager, Super Admin | AI Agent, Supplier, Patient |
| Payroll readiness | Manager, HR/Payroll, Finance, Super Admin | AI Agent, regular staff |
| Leave request | Manager, HR/Payroll, Super Admin | AI Agent, requester |
| Contract acknowledgement | Assigned signer, HR verification, Super Admin | AI Agent |
| Training completion review | Manager, HR/Payroll, Compliance, Super Admin | AI Agent |
| Inventory reorder | Inventory, Manager, Super Admin | AI Agent final approval |
| Incident closure | Manager, Compliance, Super Admin | AI Agent, reporter unless manager |
| Privacy breach closure | Compliance, Super Admin | AI Agent, regular staff |

## Object-Level Access Rules

- `branch_id` scopes most operational records.
- `assigned_user_id`, `created_by_id`, and `responsible_user_id` grant limited staff access.
- `entity.owner_user_id` grants own-profile or own-entity access.
- Supplier and contractor access is restricted to their own entity and assigned tickets.
- Patient records are accessible only through approved operational workflows and only with minimum visible fields.
- Reports must apply the same permission filters as list/detail APIs.

## Phase 2 Implementation Notes

- Use a custom Django user model from the first migration.
- Represent role membership separately from Django groups so domain role metadata can evolve.
- Keep Django model permissions, DRF permissions, object-level filters, and audit events aligned.
- Add permission tests before building broad CRUD screens.
