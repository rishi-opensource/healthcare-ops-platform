# Phase 5 - Contracts, Consent, and Training

Phase 5 adds the compliance workspace for assigning contracts and policies, recording consent, and tracking staff training.

## Delivered

- Document assignments now support versioned templates, acknowledgement, digital signature status, expiry dates, renewal ticket links, evidence labels, and audit events.
- Consent records now track AI usage, privacy, communication, telehealth, and general consent with grant, withdrawal, expiry, subject, and scope metadata.
- Training modules and assignments now support due dates, completion, quiz score placeholder, generated certificate labels, expiry, overdue/expired states, manager review, and audit events.
- DRF endpoints expose document assignment actions, consent grant/withdraw actions, training completion/review actions, and a compliance summary endpoint.
- A Celery task refreshes expired documents/consents and overdue or expired training assignments on a recurring schedule.
- Web `/contracts` and `/training` pages now show compliance metrics, assignment detail, consent records, training modules, and action buttons.
- Mobile home now includes pending contract and training actions for staff.
- Demo seed data now includes compliance templates, assignments, consent records, and training modules.

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

OpenAPI generation completed with non-blocking path parameter warnings for the new action routes and no errors.
