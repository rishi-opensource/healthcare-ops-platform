# Phase 3 - Universal Tickets Vertical Slice

Phase 3 turns the ticket foundation into a usable operational workflow across API, web, and mobile.

## Backend

- Ticket lifecycle service now validates status transitions.
- Ticket actions:
  - `POST /api/v1/tickets/{id}/assign/`
  - `POST /api/v1/tickets/{id}/comments/`
  - `POST /api/v1/tickets/{id}/transition/`
  - `POST /api/v1/tickets/{id}/complete/`
  - `POST /api/v1/tickets/{id}/request-approval/`
  - `POST /api/v1/tickets/{id}/approvals/{approval_id}/review/`
  - `GET /api/v1/tickets/summary/`
- Permission-filtered ticket queries:
  - Privileged roles can see branch-scoped tickets.
  - Non-privileged users only see tickets they created or are assigned.
  - Mobile can request assigned tasks with `assigned_to=me`.
- Ticket completion creates task completion metadata and a pending approval when requested.
- Approval review moves tickets to completed or needs correction.
- Ticket comments, assignment, completion, approval request, approval review, creation, and transition actions create audit events.
- `seed_demo` now creates manager/reception users and two demo tickets.

## Web

- `/tickets` is now an API-backed workspace with:
  - Status-filtered queue.
  - Summary metric strip.
  - Ticket detail panel.
  - Create ticket form.
  - Assignment control.
  - Lifecycle transition controls.
  - Completion form.
  - Approval approve/correction controls.
  - Timeline and internal notes.
- `/dashboard` now reads ticket summary counts instead of static placeholder metrics.

## Mobile

- Mobile Tasks tab now loads assigned tickets from the API.
- Users can start a task, request correction, and complete with a summary.
- Assigned task list uses the shared API client and secure token hydration.

## Verification

Commands run successfully:

```bash
.venv/bin/python apps/api/manage.py check
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py test apps/api/tests
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
npm run typecheck
npm run lint
npm --workspace @healthcare/web run build
curl -sS http://127.0.0.1:8000/api/v1/health/
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/login/ -H 'Content-Type: application/json' -d '{"email":"admin@healthcare.local","password":"ChangeMe123!"}'
curl -sS http://127.0.0.1:8000/api/v1/tickets/ -H 'Authorization: Token <token>'
curl -sS http://127.0.0.1:8000/api/v1/tickets/summary/ -H 'Authorization: Token <token>'
curl -sS http://127.0.0.1:3000/tickets
```

## Running Locally

```bash
docker compose up -d postgres redis
export DATABASE_URL=postgresql://healthcare:healthcare@127.0.0.1:55432/healthcare
.venv/bin/python apps/api/manage.py runserver 127.0.0.1:8000
npm --workspace @healthcare/web run dev
npm --workspace @healthcare/mobile run start
```

Demo logins:

```text
admin@healthcare.local / ChangeMe123!
manager@healthcare.local / ChangeMe123!
reception@healthcare.local / ChangeMe123!
```

## Notes

- Attachment upload storage exists from Phase 2, but Phase 3 web/mobile evidence upload UI is still minimal. The workflow records comments, completion notes, approvals, and audit events; rich file evidence can be expanded in the document/evidence phase.
- In-app browser visual verification was not available in this environment, so verification used production build and HTTP smoke tests.
