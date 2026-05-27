# Agent Guidance

This repository is `healthcare-ops-platform`, the Healthcare Doctors Adaptive Healthcare OS: a healthcare operations monorepo with a Django/DRF API, Next.js web app, Expo mobile app, product requirements, presentation visuals, and shared TypeScript packages.

GitHub remote:

```text
git@github.com:rishi-opensource/healthcare-ops-platform.git
```

## Current Project State

- Canonical requirements: `docs/requirements.md`
- Original PRD source: `req.txt`
- DevBrain project: `/Users/rishi/DevBrain/Projects/healthcare-doctors-os/`
- DevBrain plan: `/Users/rishi/DevBrain/Projects/healthcare-doctors-os/plan.md`
- DevBrain state: `/Users/rishi/DevBrain/Projects/healthcare-doctors-os/state.md`
- Current phase: Phase 5 - Contracts, Consent, and Training
- Completed phases: Phase 1 docs, Phase 2 scaffold, Phase 3 ticket vertical slice, Phase 4 entity registry and onboarding
- Product visuals for presentation: `docs/product-visuals/`

## Project Shape

- `apps/api` contains the Django 5.2 + DRF backend.
- `apps/web` contains the Next.js App Router web UI.
- `apps/mobile` contains the Expo Router mobile UI.
- `packages/api-client` contains the shared TypeScript API client and generated OpenAPI schema types.
- `packages/ui` contains shared labels, status tones, role labels, and design tokens.
- `packages/config` contains shared TypeScript config.
- `docs/phase-*` contains product, architecture, privacy, and implementation history. Read these before making broad feature changes.
- `docs/requirements.md` is the current product-team requirements summary and should be checked before changing feature scope.
- `docs/product-visuals/` contains product-team presentation images for the dashboard, mobile workspace, universal ticket workflow, and ecosystem map.

## Product Boundaries

- This is an operations platform, not an EHR.
- Do not add clinical records, diagnoses, prescriptions, pathology, treatment plans, Medicare details, My Health Record data, vitals, allergies, medications, or detailed health history unless the user explicitly asks and the privacy design is updated.
- Patient-related data in MVP scope must stay operational: references, masked contact metadata, appointment/ticket context, consent status, communication summaries, incident links, and check-in references.
- Prefer branch-scoped, role-scoped, and audit-friendly workflows for sensitive data.
- Avoid storing full call transcripts or free-text clinical information in ticket notes.
- Voice AI transcripts, confidence scores, and action logs are in scope only as operational/audit controls; avoid collecting unnecessary clinical content.

## Product Requirements To Preserve

- Every important activity should be ticketed, traceable, approved where needed, and reportable.
- Core workflows include users/roles, universal tickets, entity onboarding, contracts, consent, training, dashboard/reporting, roster/leave/attendance, payroll readiness, inventory/procurement/barcode, incidents, communication, AI review, web UI, and mobile UI.
- Expanded scope includes configurable workflows/rules, voice AI audit controls, emergency/access workflows, daily workspace, shift handover, offline continuity, data governance, event history, observability, backup/recovery, data retention, integration readiness, healthcare interoperability planning, and AI governance.
- Future enterprise readiness includes master data governance, event-driven automation, rule engine support, workforce intelligence, risk/fraud monitoring, FHIR/HL7/SNOMED CT/ICD-10 readiness where clinically relevant, advanced AI supervision, and modular platform boundaries.
- Treat emergency, visitor/access, offline, voice AI, and healthcare interoperability requirements as product-confirmed before making them first-launch blockers.

## Backend Conventions

- Use existing Django apps and service patterns before adding new apps or abstractions.
- Keep business workflow logic in service modules when it spans models, permissions, audit events, or lifecycle transitions.
- Keep DRF serializers explicit and avoid exposing model fields by default.
- Maintain audit/event-history coverage for meaningful workflow mutations.
- Prefer configurable workflow templates, approval rules, escalation rules, and due-date rules where the existing model supports it or the feature scope justifies it.
- Preserve token auth endpoints and role-aware access patterns.
- Migrations are source files; do not edit applied migration history casually. Add new migrations for model changes.
- Generated or cache artifacts such as `__pycache__`, `.ruff_cache`, and local database/media files should not be part of intentional source edits.

Useful backend commands:

```bash
.venv/bin/python apps/api/manage.py check
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py test apps/api/tests
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
```

Local backend services:

```bash
docker compose up -d postgres redis
export DATABASE_URL=postgresql://healthcare:healthcare@127.0.0.1:55432/healthcare
.venv/bin/python apps/api/manage.py runserver 127.0.0.1:8000
```

Demo users:

```text
admin@healthcare.local / ChangeMe123!
manager@healthcare.local / ChangeMe123!
reception@healthcare.local / ChangeMe123!
```

## Frontend Conventions

- Web uses Next.js App Router under `apps/web/app`.
- Mobile uses Expo Router under `apps/mobile/app`.
- Prefer shared API/client helpers and shared labels from `packages/api-client` and `packages/ui`.
- Keep operational UIs dense, readable, and work-focused. Avoid marketing-page patterns for app screens.
- Preserve role-aware navigation and branch/workflow context.
- For frontend changes, check both desktop web and mobile ergonomics when the workflow spans both apps.
- Product UI should support the platform story in `docs/requirements.md`: super admin command center, staff daily workspace, ticket detail drilldowns, approval/audit visibility, and mobile-first task completion.
- Mobile staff flows should account for voice, scan, roster, leave, handover, training, policy acknowledgement, stock alerts, incident capture, and payroll readiness when those modules are in scope.

Useful frontend commands:

```bash
npm run typecheck
npm run lint
npm --workspace @healthcare/web run build
npm --workspace @healthcare/web run dev
npm --workspace @healthcare/mobile run start
```

## API Client And Schema

- API schema generation expects the backend running at `http://127.0.0.1:8000`.
- Regenerate schema/types when API response shapes or endpoints change.
- Do not hand-edit generated schema/type output when it can be regenerated from the backend.

```bash
npm run generate:api
```

## Verification Expectations

- For backend-only changes, run Django checks, Ruff, and focused tests at minimum.
- For API contract changes, also regenerate/check the OpenAPI schema and run TypeScript typecheck.
- For web/mobile changes, run relevant workspace typechecks and build when feasible.
- For cross-stack workflow changes, smoke test login plus the affected API endpoints and UI routes.
- For requirements/docs/presentation changes, verify file links and keep DevBrain plan/state aligned when project phase or scope changes.
- If a check cannot be run, state the reason and what remains unverified.

## Known Caveats

- Current Next/Expo dependency trees have known moderate `npm audit` findings in transitive dependencies. Do not run `npm audit fix --force` without reviewing the resulting package changes.
- Existing generated folders such as `node_modules`, `.next`, `.ruff_cache`, and `__pycache__` may be present locally. Avoid reading or editing them unless directly relevant.
- Rich file evidence upload UI is still minimal; document/attachment storage exists and is expected to expand in Phase 5.
- Emergency, visitor/access, offline continuity, voice AI, and interoperability scope need product confirmation before they are treated as launch blockers.

## Working Style

- Use `rg` or `rg --files` for repository search.
- Keep changes scoped to the requested workflow or defect.
- Follow existing models, serializers, services, and UI patterns before inventing new ones.
- Do not revert unrelated local changes.
- Prefer non-destructive commands. Ask before any GitHub or Google Workspace write operation.
- When updating scope or phases, update both repository docs and `/Users/rishi/DevBrain/Projects/healthcare-doctors-os/` where relevant.
