# Phase 4 - Entity Registry and Onboarding

Phase 4 adds onboarding workflows for human and non-human entities.

## Backend

- Entity registry now supports typed profile creation for staff, suppliers, patient references, assets, inventory items, and AI agents.
- Entities receive generated QR/barcode values when one is not supplied.
- Added entity lifecycle history with audit coverage.
- Added onboarding workflow templates, step templates, onboarding runs, and step completions.
- Starting onboarding creates:
  - Step completion records from the selected workflow template.
  - Document assignments for document steps.
  - Tickets for ticket-backed onboarding steps.
  - An activation review ticket.
- Completing all required steps moves onboarding to waiting approval.
- Activation requires all required steps to be completed, verified, or waived.

## API

- `GET /api/v1/entities/`
- `POST /api/v1/entities/`
- `GET /api/v1/entities/summary/`
- `POST /api/v1/entities/{id}/transition/`
- `POST /api/v1/entities/{id}/start-onboarding/`
- `POST /api/v1/entities/{id}/complete-onboarding-step/`
- `POST /api/v1/entities/{id}/activate/`
- `GET /api/v1/onboarding-workflow-templates/`

## Web

- `/entities` is now an entity registry workspace with:
  - Entity list and status filter.
  - Detail panel with QR identifier, responsible user, lifecycle, and onboarding progress.
  - Entity creation form.
  - Start onboarding and activate actions.
- `/onboarding` now shows onboarding metrics and in-progress workflows.

## Mobile

- Mobile Home tab now shows onboarding workload metrics.
- Staff can inspect onboarding entities and complete the next pending onboarding step with a note.

## Demo Seed Data

`seed_demo` now creates:

- Privacy and supplier document templates.
- Staff, supplier, and inventory onboarding workflow templates.
- Demo employee, supplier, and inventory item entities.
- Onboarding steps, document assignments, and activation tickets for demo entities.

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
curl -sS http://127.0.0.1:8000/api/v1/entities/ -H 'Authorization: Token <token>'
curl -sS http://127.0.0.1:8000/api/v1/entities/summary/ -H 'Authorization: Token <token>'
curl -sS http://127.0.0.1:3000/entities
```

## Notes

- File upload UI for onboarding evidence remains a later expansion. Phase 4 records document assignments, evidence labels, tickets, notes, and audit events.
- Browser screenshot verification was not available in this environment, so verification used build and HTTP smoke tests.
