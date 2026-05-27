# Phase 2 - Backend and UI Foundations

Phase 2 creates the runnable foundation for parallel backend/UI delivery.

## Implemented Structure

```text
apps/
  api/        Django + DRF API foundation
  web/        Next.js web shell
  mobile/     Expo mobile shell
packages/
  api-client/ shared TypeScript API client and generated schema location
  ui/         shared role/status labels and design tokens
  config/     shared TypeScript config
```

## Backend Foundation

- Django 5.2 LTS project with PostgreSQL local default through `DATABASE_URL`.
- DRF token auth endpoints:
  - `POST /api/v1/auth/login/`
  - `POST /api/v1/auth/logout/`
  - `GET /api/v1/auth/me/`
- Public health endpoint: `GET /api/v1/health/`.
- OpenAPI schema: `GET /api/schema/`.
- Swagger UI: `GET /api/docs/`.
- Custom user model, roles, role assignments, organizations, branches.
- Append-only audit event model and audit service.
- Entity registry with typed profiles.
- Ticket foundation with numbering, status history, comments, attachments, approvals, task completions, and transitions.
- Document template, file, and assignment metadata.
- Demo seed command:

```bash
.venv/bin/python apps/api/manage.py seed_demo
```

Seeded demo login:

```text
admin@healthcare.local / ChangeMe123!
```

## Web Foundation

- Next.js App Router shell.
- Login page wired to DRF auth.
- Role-aware sidebar navigation.
- Command dashboard placeholder connected to API health.
- Route shells for tickets, users, entities, onboarding, contracts, training, roster, leave, attendance, payroll readiness, inventory, procurement, incidents, communications, AI review, reports, audit, and settings.

## Mobile Foundation

- Expo Router shell.
- Login screen wired to shared API client and secure token storage.
- Tab navigation for Home, Tasks, Scan, Roster, and Profile.
- Barcode/QR scan placeholder using Expo Camera.
- Mobile task, roster, and profile placeholders for future vertical slices.

## Verification

Commands run successfully:

```bash
.venv/bin/python apps/api/manage.py check
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py test apps/api/tests
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
npm run lint
npm run typecheck
npm --workspace @healthcare/web run build
curl -sS http://127.0.0.1:8000/api/v1/health/
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/login/ -H 'Content-Type: application/json' -d '{"email":"admin@healthcare.local","password":"ChangeMe123!"}'
curl -sS http://127.0.0.1:3000/dashboard
```

## Known Caveat

`npm audit --audit-level=moderate` reports moderate transitive issues inside current Next/Expo dependency trees:

- `postcss <8.5.10` through Next.
- `uuid <11.1.1` through Expo config tooling.

`npm audit fix` did not resolve these without breaking-force changes. Do not run `npm audit fix --force` unless the package downgrades are reviewed.

## Running Locally

```bash
docker compose up -d postgres redis
export DATABASE_URL=postgresql://healthcare:healthcare@127.0.0.1:55432/healthcare
.venv/bin/python apps/api/manage.py runserver 127.0.0.1:8000
npm --workspace @healthcare/web run dev
npm --workspace @healthcare/mobile run start
```
