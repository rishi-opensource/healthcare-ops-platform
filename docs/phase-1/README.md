# Phase 1 - Scope, Architecture, UX Flows

This folder is the Phase 1 source of truth for the Healthcare Doctors Adaptive Healthcare OS. It turns `req.txt` and the saved DevBrain plan into implementation-ready decisions for Phase 2.

## Deliverables

- [mvp-scope.md](mvp-scope.md) - MVP modules, deferred scope, acceptance criteria, and launch assumptions.
- [roles-permissions.md](roles-permissions.md) - role hierarchy, permission model, approval limits, and access-control defaults.
- [patient-data-boundary.md](patient-data-boundary.md) - what patient information the MVP can store, what stays out, and privacy controls.
- [domain-model.md](domain-model.md) - core Django apps, entities, relationships, and model ownership.
- [api-ui-architecture.md](api-ui-architecture.md) - Django/DRF, Next.js, Expo, OpenAPI, testing, and delivery architecture.
- [ux-flows.md](ux-flows.md) - web/mobile sitemap, primary workflows, and design-system baseline.

## Phase 1 Completion Criteria

- MVP scope is explicit enough to avoid building every PRD item at once.
- Role and permission defaults are defined before auth is scaffolded.
- Patient data boundaries are conservative and implementation-ready.
- Core model names and app boundaries are clear enough to create migrations.
- Web and mobile UI work can start in Phase 2 alongside the backend.
- Each future feature is framed as a vertical slice: model, API, permission, audit, web UI, mobile UI where relevant, and tests.

## Current Status

Phase 1 is a planning/design implementation phase. No production app code is expected here. Phase 2 starts the monorepo and application scaffolds.
