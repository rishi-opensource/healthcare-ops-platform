# Healthcare Doctors OS - Requirements Summary

## 1. Product Goal

Healthcare Doctors OS is a mobile-first healthcare operations platform for running clinic work in one place.

The platform should help the team manage tasks, onboarding, contracts, training, rosters, payroll readiness, inventory, incidents, compliance, and AI-assisted workflows.

The core product rule is simple:

> Every important activity should be ticketed, traceable, approved where needed, and available for reporting.

## 2. Target Users

- Super Admin: monitors the full business, approvals, reports, users, tickets, payroll readiness, inventory, compliance, and AI activity.
- Clinic Manager: manages day-to-day operations, rosters, staff work, approvals, and escalations.
- HR / Payroll Admin: manages onboarding, documents, training, leave, attendance, timesheets, and payroll readiness.
- Finance / Accounts User: manages payment approvals, supplier payments, expenses, and financial controls.
- Compliance Officer: monitors policies, consent, training, incidents, audit history, and compliance risks.
- Receptionist / Staff: completes daily mobile tasks, tickets, handovers, training, leave requests, stock scans, and incident reports.
- Doctors / Practitioners: manage assigned work, patient-related tasks, documentation, follow-ups, and compliance items.
- Inventory / Procurement User: manages stock, barcode scanning, suppliers, purchase orders, deliveries, and reorder alerts.
- Suppliers / Contractors / AI Agents / Assets: tracked as entities that can be onboarded, assigned work, audited, and linked to tickets.

## 3. Functional Requirements

### 3.1 User, Role, and Access Management

- The system must support role-based access for admins, managers, HR, finance, compliance, clinical users, receptionists, inventory users, contractors, and AI agents.
- Users must only see information and actions allowed by their role and branch.
- Admins must be able to view users, roles, activity, tickets, onboarding status, and audit history.

### 3.2 Universal Ticket System

- Users must be able to create, assign, update, complete, approve, and review tickets.
- Tickets must support status, priority, due date, assignee, related entity, notes, comments, evidence, approval history, and audit trail.
- Tickets must be usable for onboarding, payroll checks, inventory issues, incidents, leave requests, supplier issues, maintenance, AI-created tasks, and general operations.

### 3.3 Entity Registry and Onboarding

- The system must track people and non-human entities, including staff, suppliers, contractors, patients where relevant, assets, inventory items, branches, and AI agents.
- Entities must support onboarding workflows, document requirements, QR/barcode identifiers, activation status, lifecycle history, and responsible owner.
- Onboarding steps must be trackable and linked to tickets or document assignments where needed.

### 3.4 Contracts, Consent, and Training

- The system must support document templates, contract assignments, policy acknowledgements, consent records, signatures or evidence, expiry dates, and renewal reminders.
- Training modules must support assignment, completion, certificates or proof, expiry status, overdue status, and manager review.
- Compliance users must be able to see missing, expired, or overdue items.

### 3.5 Dashboard and Reporting

- Super admins and managers must have dashboards showing open tickets, completed work, overdue tasks, payroll pending, roster status, leave requests, inventory alerts, contract alerts, training alerts, incidents, compliance risks, and AI activity.
- Dashboard numbers must be clickable and show detailed records.
- Reports must support filtering by user, role, branch, date, status, and category.

### 3.6 Roster, Leave, Attendance, and Payroll Readiness

- Staff must be able to view rosters, shifts, leave status, assigned work, and completed tasks.
- Managers must be able to approve leave, review attendance, check timesheets, and mark work as payroll-ready.
- Payroll readiness must be linked to verified work, attendance, approvals, and completed tickets.

### 3.7 Inventory, Procurement, and Barcode Workflows

- Users must be able to scan barcodes or QR codes for stock, assets, deliveries, forms, and tracked items.
- The system must support stock levels, batch numbers, expiry dates, stock movements, delivery checks, damaged goods, transfers, suppliers, purchase orders, and reorder alerts.
- Inventory actions must be linked to users, locations, tickets, and audit history.

### 3.8 Incidents, Communication, and AI Review

- Users must be able to report incidents with category, priority, evidence, follow-up actions, assignment, and closure status.
- Patient and business communication logs must be linkable to tickets where relevant.
- AI-created actions must be logged, reviewable by humans, and blocked from making sensitive approvals automatically.

### 3.9 Web and Mobile Apps

- The web app must support admin, manager, HR, finance, compliance, reporting, and operational workflows.
- The mobile app must support staff tasks, onboarding, tickets, scanning, roster, leave, training, handover, incident reporting, and daily work updates.
- Web and mobile must use the same backend data and keep workflow status consistent.

## 4. Non-Functional Requirements

- Security: role-based access, object-level permissions, secure authentication, and protection of sensitive healthcare and staff data.
- Auditability: important user and system actions must create audit events.
- Privacy: patient data stored in the system must be limited to the agreed operational scope.
- Reliability: the system should support daily clinic operations with clear error handling and recoverable workflows.
- Performance: dashboards, lists, and search results should load quickly for normal clinic data volumes.
- Scalability: the platform should support multiple branches, roles, workflows, entities, and future modules.
- Mobile usability: staff workflows must be easy to complete from a phone.
- Maintainability: backend, web, and mobile features should be delivered as tested vertical slices.
- Reporting accuracy: dashboard and report numbers must match underlying records.
- Compliance readiness: contracts, training, consent, incidents, approvals, and audit trails must be easy to review.

## 5. Current Project Status

- Phase 1 complete: scope, architecture, roles, patient data boundary, domain model, and UX flows.
- Phase 2 complete: backend, web, mobile, auth, navigation, API docs, seed data, and test foundation.
- Phase 3 complete: universal ticket workflow across API, web, and mobile.
- Phase 4 complete: entity registry and onboarding workflow.
- Current phase: Phase 5, contracts, consent, and training.

## 6. MVP Priorities

The MVP should focus on:

- Role-based login and navigation.
- Universal tickets with assignment, completion, approval, and audit history.
- Entity onboarding for staff, suppliers, assets, inventory items, and AI agents.
- Contracts, policies, consent, and training tracking.
- Super admin dashboard and operational reporting.
- Staff mobile workflows for daily tasks, onboarding, roster, leave, scanning, and incidents.
- Inventory and barcode workflows for stock and assets.
- Payroll readiness based on verified work and approvals.

## 7. Open Questions for Product Team

- Which modules are mandatory for first launch?
- What exact patient information can be stored in the MVP?
- Which roles and approval limits should be active on day one?
- What payroll rules should apply to staff, contractors, and practitioners?
- Which contract, policy, consent, and training templates are approved?
- Which barcode formats and physical labels should be used?
- Which external systems must be integrated before launch?
