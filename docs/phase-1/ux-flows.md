# UX Flows

## Product UI Principle

The product UI is the Next.js web app and Expo mobile app. Django Admin is only support tooling for operators and developers.

Build dense, operational screens. This is a healthcare operations system, not a marketing site. Prioritize fast scanning, clear status, role-relevant tasks, approvals, and drilldowns.

## Web Sitemap

```text
/login
/dashboard
/tickets
/tickets/new
/tickets/[ticketId]
/users
/users/[userId]
/entities
/entities/[entityId]
/onboarding
/contracts
/training
/roster
/leave
/attendance
/payroll-readiness
/inventory
/inventory/[itemId]
/procurement
/incidents
/incidents/[incidentId]
/communications
/ai-review
/reports
/audit
/settings/roles
/settings/branches
```

## Mobile Sitemap

```text
/login
/home
/tasks
/tasks/[ticketId]
/tickets/new
/scan
/roster
/leave
/handover
/training
/documents
/inventory/item
/incident/new
/payroll-status
/profile
```

## Role-Based Landing Screens

| Role | Web landing | Mobile landing |
|------|-------------|----------------|
| Super Admin | Command dashboard | Alerts and approvals summary |
| Manager | Team operations dashboard | Approvals, incidents, roster alerts |
| HR/Payroll | Onboarding/payroll readiness | Approvals summary |
| Finance | Finance/payroll reports | Review queue if needed |
| Compliance | Compliance dashboard | Incident/compliance alerts |
| Receptionist | Task queue if using web | Daily tasks, scan, roster, handover |
| Doctor | Appointment/task summary | Assigned patient-related tasks |
| Nurse | Clinical support tasks | Treatment-room tasks, incidents, stock |
| Pharmacist | Medication/inventory dashboard | Scan, expiry, controlled item tasks |
| Inventory | Inventory dashboard | Scan, deliveries, reorder tasks |

## Primary Web Flows

### Super Admin Dashboard

1. Sign in.
2. View cards for open tickets, completed tickets, overdue work, payroll pending, users working, roster, leave, inventory, contracts, training, incidents, AI activity, and compliance risk.
3. Click a card to drill into a filtered list.
4. Open user detail.
5. Review completed task summary by ticket number.
6. Open ticket detail and audit timeline.
7. Add appraisal feedback or payroll-link approval.
8. Export report.

### Manager Ticket Approval

1. Open approvals queue.
2. Filter by branch, due date, category, and staff member.
3. Open completed ticket.
4. Review timeline, evidence, notes, AI involvement, and completion summary.
5. Approve, reject, or request correction.
6. Add feedback and payroll-readiness decision if applicable.

### HR Onboarding

1. Create staff/contractor/supplier entity.
2. Assign role, branch, onboarding template, contract templates, and training modules.
3. Upload or request documents.
4. Track checklist completion.
5. Approve activation when requirements are complete.

### Compliance Review

1. Open compliance dashboard.
2. Review overdue training, expired contracts, incidents, privacy events, and AI actions.
3. Open record detail and audit trail.
4. Request follow-up or close compliance item with approval.

## Primary Mobile Flows

### Receptionist Daily Work

1. Sign in.
2. View home screen with current shift, assigned tickets, urgent items, scan shortcut, leave, handover, and payroll status.
3. Open assigned task.
4. Update status, add note, attach evidence, or complete task.
5. Create new ticket from shortcut or voice draft.
6. Submit shift handover before clock-out.

### Barcode/QR Scan

1. Tap scan.
2. Camera opens with scan target.
3. App resolves barcode through API.
4. Show resolved item, ticket, delivery, asset, patient reference, staff ID, or form.
5. User selects action: update stock, verify delivery, report issue, create ticket, attach evidence, or escalate.
6. Result creates stock movement/ticket/audit event as applicable.

### Leave Request

1. Open leave.
2. View balance and upcoming shifts.
3. Select leave type and dates.
4. Add reason and submit.
5. System creates leave request ticket.
6. Manager approves or rejects.

### Incident Report

1. Tap incident.
2. Choose category and priority.
3. Enter operational summary.
4. Attach evidence if needed.
5. Submit.
6. System creates incident and linked ticket, assigns responsible manager, and logs audit event.

## Design System Baseline

### Navigation

- Web uses a persistent sidebar for admin/manager roles.
- Mobile uses tab navigation for Home, Tasks, Scan, Roster, and Profile.
- Role-specific secondary actions are visible only where permitted.

### Components

- Status badges for ticket, onboarding, contract, training, leave, payroll readiness, inventory, and incident states.
- Data tables on web with filters, saved views later, and export buttons where permitted.
- Mobile cards for assigned work and urgent alerts.
- Approval panels with decision buttons, notes, evidence preview, and timeline.
- Timeline component for ticket/audit history.
- Scanner action sheet for barcode outcomes.
- Empty, loading, offline, and permission-denied states for every screen.

### Visual Direction

- Quiet, utilitarian, dense healthcare operations UI.
- Avoid decorative hero layouts, marketing cards, and visual clutter.
- Clear status colors, restrained palette, strong typography hierarchy, and high contrast.
- Tables and mobile cards should optimize for scanning and repeated use.

## API/UI Contract Rules

- UI list screens must use paginated APIs.
- UI detail screens must have explicit DTOs, not raw model dumps.
- Mutations must return the updated resource and audit/timeline update where practical.
- Forms must validate client-side with Zod and server-side with DRF serializers.
- Permission-denied responses must be handled as normal UI states.
- Web and mobile labels should use the same domain language as API enums.

## Phase 2 UI Foundation Tasks

- Create shared design tokens and domain status map.
- Build login layout and role-aware navigation.
- Build placeholder dashboard, task list, and scan shell.
- Generate API client from placeholder OpenAPI schema.
- Add MSW/fixtures for Phase 3 ticket screens if backend endpoints are not ready.
