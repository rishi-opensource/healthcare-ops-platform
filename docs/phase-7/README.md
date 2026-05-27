# Phase 7 - Roster, Leave, Attendance, Payroll Readiness

Phase 7 adds workforce operations for shift planning, leave approvals, attendance capture, handover notes, and payroll-ready timesheet review.

## Delivered

- Workforce API app with shifts, leave requests, attendance records, handover notes, and timesheet summaries.
- Shift publication, leave approval/rejection, clock-in/out, attendance approval, handover acknowledgement, timesheet refresh, submission, and review actions.
- Audit events for sensitive workforce actions.
- Shared TypeScript client coverage for roster, leave, attendance, handover, timesheet, and workforce summary endpoints.
- Web `/roster`, `/leave`, `/attendance`, and `/payroll-readiness` workspaces now load live workforce data and expose manager actions.
- Mobile Home now includes shift/attendance, payroll-ready, and handover metrics plus a clock-in/out action.
- Demo seed data now includes a published shift, leave request, attendance record, handover note, and submitted timesheet.
- Focused tests cover the Phase 7 workforce workflow.

## Verification

```bash
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py makemigrations --check --dry-run
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py test tests
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
npm run lint
npm run typecheck
npm --workspace @healthcare/web run build
```

OpenAPI generation completed with non-blocking action path parameter warnings and no errors.
