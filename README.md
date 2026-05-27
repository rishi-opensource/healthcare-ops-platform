# Healthcare Doctors Adaptive Healthcare OS

Mobile-first healthcare operations platform with a Django/DRF backend, Next.js web UI, and Expo mobile UI.

## Phase 2 Scope

Phase 2 creates the runnable foundation:

- `apps/api` - Django REST Framework API with auth, roles, branches, audit events, entities, tickets, documents, OpenAPI, seed data, and tests.
- `apps/web` - Next.js shell with login, role-aware navigation, dashboard placeholders, and API client wiring.
- `apps/mobile` - Expo shell with auth, tab navigation, task/home/scan placeholders, and API client wiring.
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
