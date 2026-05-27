# Phase 6 - Dashboard and Reporting MVP

Phase 6 adds the first reporting layer for operational visibility across tickets, entities, compliance, training, and completed staff tasks.

## Delivered

- Dashboard report API with ticket workload, overdue work, pending approvals, entity onboarding, workforce activity, operations, compliance, and daily workspace metrics.
- User completed-task summary API with total tasks, minutes, payroll-ready tasks, correction requests, and appraisal feedback counts.
- Export preview API for ticket status and user-task reports.
- Ticket review actions for appraisal feedback, correction requests, and payroll-link approval.
- Web `/dashboard` now shows live command metrics, daily workspace signals, and compliance summaries.
- Web `/reports` now shows user completed-task summaries and an export preview.
- Mobile Home now includes Phase 6 daily workspace and manager summary metrics.
- Demo seed data now includes a completed task with appraisal and payroll readiness.

## Verification

```bash
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py makemigrations --check --dry-run
.venv/bin/python apps/api/manage.py test tests
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
npm run lint
npm run typecheck
npm --workspace @healthcare/web run build
```

OpenAPI generation completed with the existing non-blocking document action path parameter warnings and no errors.
