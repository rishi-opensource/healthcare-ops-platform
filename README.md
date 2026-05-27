# Healthcare Doctors Adaptive Healthcare OS

Mobile-first healthcare operations platform with a Django/DRF backend, Next.js web UI, and Expo mobile UI.

## Current Scope

The project is implemented through Phase 8:

- `apps/api` - Django REST Framework API with auth, roles, branches, audit events, entities, tickets, documents, consent, training, dashboard reports, workforce operations, inventory/procurement, barcode resolution, task summaries, OpenAPI, seed data, and tests.
- `apps/web` - Next.js shell with login, role-aware navigation, tickets, entity registry, onboarding, contracts, training, command dashboard, reports, roster, leave, attendance, payroll readiness, inventory, and procurement.
- `apps/mobile` - Expo shell with auth, tab navigation, ticket/task actions, onboarding actions, contract/training acknowledgement flows, daily workspace metrics, attendance actions, and barcode resolution.
- `packages/api-client` - shared TypeScript API client entrypoint.
- `packages/ui` - shared status labels, role labels, and design tokens.
- `packages/config` - shared TypeScript config.

## Local Setup

Backend:

```bash
python3 -m venv .venv
.venv/bin/pip install -r apps/api/requirements.txt
docker compose up -d postgres redis
export DATABASE_URL=postgresql://healthcare:healthcare@127.0.0.1:55432/healthcare
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py runserver 127.0.0.1:8000
```

Web/mobile dependencies:

```bash
npm install
npm run dev:web
npm run dev:mobile
```

Useful checks:

```bash
.venv/bin/python apps/api/manage.py test
npm run typecheck
```

## Phase 1 References

- [MVP scope](docs/phase-1/mvp-scope.md)
- [Roles and permissions](docs/phase-1/roles-permissions.md)
- [Patient data boundary](docs/phase-1/patient-data-boundary.md)
- [Domain model](docs/phase-1/domain-model.md)
- [API and UI architecture](docs/phase-1/api-ui-architecture.md)
- [UX flows](docs/phase-1/ux-flows.md)

## Phase References

- [Phase 2 foundation](docs/phase-2/README.md)
- [Phase 3 tickets](docs/phase-3/README.md)
- [Phase 4 entity registry and onboarding](docs/phase-4/README.md)
- [Phase 5 contracts, consent, and training](docs/phase-5/README.md)
- [Phase 6 dashboard and reporting](docs/phase-6/README.md)
- [Phase 7 roster, leave, attendance, payroll readiness](docs/phase-7/README.md)
- [Phase 8 inventory, procurement, and barcode](docs/phase-8/README.md)
