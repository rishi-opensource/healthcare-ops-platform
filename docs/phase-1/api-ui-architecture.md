# API and UI Architecture

## Repository Shape

Phase 2 should scaffold the repo as:

```text
apps/
  api/        Django + DRF backend
  web/        Next.js web app
  mobile/     Expo React Native mobile app
packages/
  api-client/ generated TypeScript API client from DRF OpenAPI
  ui/         shared tokens and cross-platform design references
  config/     shared TypeScript, lint, formatting, and environment docs
docs/
  phase-1/
```

## Backend Stack

- Python 3.13
- Django 5.2 LTS
- Django REST Framework
- PostgreSQL 17+
- Celery
- Redis
- drf-spectacular for OpenAPI
- pytest and pytest-django
- factory-boy for test data
- Ruff for lint/format
- Docker Compose for local development

## Web Stack

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod
- Recharts for dashboard charts
- Playwright for E2E

## Mobile Stack

- Expo React Native
- TypeScript
- Expo Router
- NativeWind
- Expo Camera for barcode/QR scanning
- TanStack Query
- React Hook Form
- Zod

## API Contract Strategy

- DRF owns the API contract.
- drf-spectacular generates OpenAPI schema from serializers and viewsets.
- `packages/api-client` generates TypeScript types/client from OpenAPI.
- Web and mobile use the generated client, not hand-built fetch wrappers.
- API changes should be backward-compatible within `/api/v1/`.
- Breaking changes require versioned endpoints or explicit migration.

## Endpoint Conventions

Use REST resources with custom actions for workflows:

```text
/api/v1/auth/
/api/v1/users/
/api/v1/roles/
/api/v1/entities/
/api/v1/tickets/
/api/v1/tickets/{id}/transition/
/api/v1/tickets/{id}/approve/
/api/v1/tickets/{id}/request-correction/
/api/v1/documents/
/api/v1/training/
/api/v1/roster/
/api/v1/leave-requests/
/api/v1/attendance/
/api/v1/payroll-readiness/
/api/v1/inventory/
/api/v1/barcodes/resolve/
/api/v1/incidents/
/api/v1/communications/
/api/v1/ai-actions/
/api/v1/reports/
```

## Backend Layering

```text
models.py       data shape and constraints
selectors.py    read/query logic
services.py     workflow mutations and audit calls
serializers.py  DTO validation and representation
permissions.py  role and object-level checks
views.py        DRF viewsets/actions
tasks.py        Celery jobs
tests/          unit and API tests
```

Use service functions for business transitions such as approving tickets, closing incidents, payroll readiness decisions, stock movements, document acknowledgements, and AI review outcomes.

## UI Delivery Model

Every feature slice must include:

1. Django model/migration.
2. DRF serializer/viewset/action.
3. Permission rules and tests.
4. Audit event coverage.
5. OpenAPI schema update.
6. Web screen.
7. Mobile screen if workflow is staff/mobile relevant.
8. E2E or manual acceptance path.

If the backend is not ready, web/mobile may use MSW or local fixtures shaped like the OpenAPI contract. Once the endpoint is available, the fixture is replaced with the generated client call.

## Authentication Flow

MVP default:
- API issues secure auth tokens or uses a battle-tested JWT/session setup selected in Phase 2.
- Web stores auth state securely and redirects by role.
- Mobile stores auth token in secure storage.
- MFA-ready fields and flows are modeled even if full MFA setup is later.

Security defaults:
- No anonymous product APIs.
- CORS locked to local dev and production hosts.
- Rate limiting for auth and sensitive workflows.
- Permission checks in every viewset.
- Reports and exports require explicit export permission.

## Audit Strategy

Audit events are appended by service functions and include:
- actor user/entity
- action
- target type and ID
- branch
- request ID
- timestamp
- IP/user agent where available
- metadata snapshot

Audit is required for:
- auth/security changes
- ticket mutations
- approvals/rejections
- document/contract/training acknowledgement
- patient-linked access or mutation
- payroll readiness actions
- stock movements
- incident and privacy workflows
- AI actions and reviews
- report exports

## Local Development Targets

- Backend: `http://127.0.0.1:8000`
- Web: `http://127.0.0.1:3000`
- Mobile: Expo dev server
- OpenAPI: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`

## Testing Baseline

Backend:
- model/service unit tests
- DRF API tests
- permission matrix tests
- audit-event tests
- Celery task tests with eager mode

Web:
- lint
- typecheck
- component tests where useful
- Playwright happy paths

Mobile:
- typecheck
- screen smoke tests where practical
- manual device tests for camera/scanning

## Deployment Direction

Preferred production target:
- AWS Sydney
- RDS PostgreSQL
- ElastiCache Redis
- S3 object storage
- ECS/Fargate or equivalent container hosting
- CloudWatch logs/alarms
- SES/SNS or approved provider for email/SMS notifications

Vercel is acceptable for web UI only if API and data residency needs remain satisfied.
