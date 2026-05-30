# ChatGPT Source Gap Analysis

Source analyzed: shared ChatGPT conversation `6a150974-ca70-83ea-b688-502412555315`, titled "Healthcare Business OS".

Compared against: `docs/requirements.md`.

## Executive Summary

The current requirements document is broadly aligned with the ChatGPT product source. It captures the main product direction: a mobile-first Healthcare Doctors operating system where entities, tickets, approvals, audit, training, contracts, inventory, payroll readiness, AI review, and reporting work together.

The main gap is not the headline scope. The gap is product depth. Many source-of-truth ideas are compressed into broad bullets, moved to future requirements, or missing acceptance detail. If implementation follows only `docs/requirements.md`, the platform may become a generic operations/ticketing app rather than the Adaptive Healthcare Operating System described in the conversation.

## Source Product Model

The ChatGPT conversation defines the product as an Adaptive Healthcare Operating System, not a normal CRM.

Core product philosophy:

- Everything is an entity.
- Every entity has identity.
- Every action creates an event.
- Every event creates an audit trail.
- Every workflow is configurable.
- Every process is observable.
- Every AI action is explainable.
- Every module is replaceable.
- Every service is API accessible.
- Everything must work mobile-first.

Core architectural model:

- Identity layer.
- Universal Entity Registry.
- Event bus / event stream.
- Workflow engine.
- Universal ticket system.
- Human actors, AI actors, and external APIs.
- Finance and contract engine.
- Compliance and audit.
- Analytics and AI intelligence.

## Visual Analysis

The shared ChatGPT Open Graph image is only a cropped visual of the original user prompt. It confirms the source topic: a CRM/operating system for Thoshi Medicals Pty Ltd, trading as Healthcare Doctors, intended to sustain the next five years with onboarding, 2FA, non-human entities, contracts, payment control, backoffice reporting, tax, and a ticketing "black box."

The repo's product visuals align with the later conversation artifacts:

- `super-admin-command-center.png` covers command center KPIs for tickets, payroll, inventory, training, AI review, incidents, compliance, and user performance.
- `mobile-staff-workspace.png` covers the receptionist/staff mobile cockpit with shift, voice, scan, tickets, roster, leave, handover, training, policy signing, stock alerts, incidents, and payroll readiness.
- `universal-ticket-workflow.png` captures the source principle that every activity becomes a ticket, with create, assign, work, evidence, approve, payroll-ready, audit, and reporting.
- `product-ecosystem-map.png` captures the broad platform modules, but it does not fully show the deeper source concepts such as event sourcing, digital twins, knowledge graph, API gateway, zero trust, document lifecycle, or AI supervisor layer.

## Major Gaps Against Requirements

### 1. AHOS Operating Constitution Is Not Explicit Enough

`docs/requirements.md` states the rule that every important activity should be ticketed and auditable, but the source conversation defines a stronger architecture constitution: entity, event, workflow, audit, API, observability, AI explainability, mobile-first, and modular replaceability.

Gap: requirements should add a named "AHOS operating principles" section and make these principles acceptance criteria for architecture and feature design.

### 2. Event Architecture Is Under-Specified

The requirements mention event history and future event-driven automation. The source treats events as a core layer between entities and workflows.

Missing details:

- event types and schema;
- event producer/consumer model;
- event replay;
- event-to-ticket triggers;
- async processing;
- webhooks;
- external integrations;
- audit use of events.

Risk: tickets may become simple CRUD records rather than a real operating system event stream.

### 3. Universal Entity Registry Needs Stronger Master Data Governance

The requirements mention stable identifiers and a single source of truth. The source is more specific: global patient ID, employee master ID, vendor master ID, SKU/GTIN, AI actor ID, immutable ticket ID, and asset registry ID.

Missing details:

- duplicate detection and merge policy;
- entity ownership;
- entity relationship model;
- lifecycle states such as recruitment, active, suspended, transferred, exited, archived;
- entity risk scores;
- digital twin state for live operational status.

### 4. Super Admin User Ecosystem Is Too High-Level

The source repeatedly refines the Super Admin dashboard around user-level task summaries, ticket references, detail links, appraisal/feedback, task detail modals, AI participation, operational impact, compliance outcome, patient impact, and audit intelligence.

The requirements only say dashboards should show completed work and detailed records.

Missing details:

- per-user completed task summaries;
- ticket number shown beside every completed task;
- task detail drilldown;
- appraisal and feedback records;
- operational quality scoring;
- AI participation indicator;
- payroll linkage per task;
- compliance and patient impact per task;
- audit trail access from task details.

### 5. Role Set Is Incomplete in `requirements.md`

The source and `docs/phase-1/mvp-scope.md` include more roles than `docs/requirements.md`.

Missing or underrepresented roles:

- Nurse / Clinical Assistant;
- Pharmacist / Medication Manager;
- Patient as operational communication target;
- External accountant;
- Lawyer/legal reviewer;
- Franchise partner / future branch operator;
- Software service/API/cloud service as non-human entities;
- Vehicles and facility devices.

### 6. AI Actor Ecosystem Needs a Taxonomy

The requirements mention AI agents and AI review, but the source defines several AI actor types:

- AI Receptionist;
- AI Billing Officer;
- AI Inventory Manager;
- AI Compliance Officer;
- AI Tax Assistant;
- AI HR Officer;
- AI Procurement Agent;
- AI Medical Scribe;
- AI Supervisor layer.

Missing details:

- AI actor registry;
- allowed and forbidden actions by AI actor;
- human approval gates;
- AI prompt/action logs;
- confidence thresholds;
- model versioning;
- override and appeal workflow;
- AI feedback loop from staff approvals/rejections.

### 7. Voice AI Is Mentioned but Not Productized

The source expects receptionist voice workflows with transcripts, replay, confidence scores, high-risk approval, multilingual support, voice biometric login, and a knowledge assistant.

The requirements mention voice input, transcripts, confidence scores, and audit history, but not:

- voice replay;
- language support;
- voice authentication policy;
- voice command risk classification;
- AI knowledge assistant screen;
- voice-driven policy/procedure Q&A;
- rejection/correction feedback to AI.

### 8. Barcode Ecosystem Is Wider Than Inventory

The requirements cover stock, assets, deliveries, forms, and tracked items. The source expands barcode/QR usage to:

- patient wristbands;
- appointment QR check-in;
- staff ID attendance;
- delivery scan;
- room/equipment maintenance;
- prescription barcode;
- asset tracking QR;
- visitor badge QR;
- consent form QR;
- ticket QR;
- contractor access QR.

Gap: barcode requirements should be generalized as a platform identification and workflow-triggering system, not only inventory support.

### 9. Contract, Consent, and Document Lifecycle Needs More Detail

The requirements cover templates, assignments, policy acknowledgements, consent, signatures, expiries, and renewals. The source is more detailed.

Missing contract types:

- employment agreement;
- medical practitioner agreement;
- independent contractor agreement;
- supplier agreement;
- AI usage and liability policy;
- patient consent and privacy agreement;
- procurement agreement;
- service level agreement;
- data processing agreement;
- franchise agreement;
- NDA;
- device/BYOD policy.

Missing document lifecycle features:

- OCR;
- versioning;
- retention policy;
- legal hold;
- document expiry;
- AI categorization;
- barcode-linked files.

### 10. Consent Management Is Too Generic

The source calls out purpose limitation and consent lifecycle.

Missing details:

- consent given;
- consent withdrawn;
- consent expiry;
- access scope;
- AI-use consent;
- third-party sharing consent;
- audit of consent changes;
- consent impact on user/AI actions.

### 11. Payments and Finance Are Softer Than the Source

The source describes one-click payment after work satisfaction, invoice generation, accounting update, tax recording, supplier payments, refunds, Medicare/insurance claims, SaaS costs, and integration candidates such as Xero, Employment Hero, Stripe, banking APIs, Dext, and Xero Tax.

The current requirements intentionally frame payroll as "payroll readiness." That is safer for MVP, but the gap should be explicit.

Missing details:

- payment execution is deferred versus payment readiness;
- invoice generation workflow;
- finance approval limits;
- export format for accounting/payroll;
- tax/BAS/GST reporting expectations;
- supplier payment approval workflow;
- refund and claim tracking boundaries.

### 12. Backoffice and Tax Reporting Need Product Boundaries

The source asks for backoffice reporting and tax. Requirements mention reporting, exports, finance controls, and future accounting integrations, but not clear backoffice modules.

Missing details:

- BAS/GST readiness reports;
- payroll export reports;
- supplier invoice reports;
- contract expiry reports;
- audit pack export;
- tax-year archival;
- accounting-system integration boundary.

### 13. Workflow and Rule Engine Needs Acceptance Detail

The source strongly says workflows and rules must not be hardcoded.

The requirements include configurable workflows and rules, but need examples as testable acceptance criteria:

- overtime approval;
- payment threshold approval;
- expiring document ticket;
- low-stock ticket;
- overdue training escalation;
- AI action requiring review;
- emergency escalation path;
- branch-specific workflow versioning.

### 14. Emergency, Incident, Visitor, and Access Workflows Need More Depth

The requirements mention emergency workflows and visitor/access workflows. The source adds:

- panic button;
- emergency broadcast;
- Code Blue workflow;
- security alert;
- patient fall;
- verbal abuse;
- medication issue;
- equipment malfunction;
- cyber incident;
- contractor sign-in;
- temporary badge printing;
- restricted access alerts.

Gap: requirements should define incident categories, escalation levels, required evidence, and closure/review states.

### 15. Communication Hub Is Under-Specified

The requirements mention SMS, email, phone notes, chat, and future messaging integrations. The source specifically calls for omnichannel patient communication:

- SMS reminders;
- WhatsApp integration;
- email confirmations;
- video calls / telehealth;
- AI chatbot escalation;
- communication-to-ticket linkage.

Gap: requirements should clarify MVP channels, future channels, message audit, consent for messaging, and staff ownership.

### 16. Workforce Intelligence and Wellbeing Are Deferred but Source-Important

The source includes performance dashboards, productivity, wait time, call metrics, appointment conversion, inventory accuracy, attendance reliability, burnout detection, wellness check-ins, recognition, and gamification.

Requirements mention workforce intelligence only as future enterprise requirements.

Gap: decide whether basic performance/appraisal analytics are MVP because Super Admin task appraisal is explicitly requested late in the source conversation.

### 17. Knowledge Graph and Digital Twin Are Missing

The source calls out a relationship engine/knowledge graph and digital twin profiles for doctors, inventory, AI agents, clinics, and suppliers.

The current requirements do not mention these except indirectly through data governance and future AI analysis.

Gap: likely not MVP implementation, but should be included as architecture-facing future requirements so current data modeling does not block it.

### 18. Zero Trust Security Is Too Broadly Expressed

The requirements mention security, role access, object-level permissions, and secure authentication. The source calls for zero trust:

- MFA;
- RBAC plus ABAC;
- device trust;
- endpoint validation;
- secrets management;
- session monitoring;
- anomaly detection;
- encryption at rest and in transit.

Gap: security requirements need specific healthcare-grade controls and acceptance criteria.

### 19. Multi-Tenant and Branch Strategy Needs Clarification

The requirements mention branches and scalability. The source talks about future branches/franchises and tenant isolation.

Missing details:

- branch versus tenant distinction;
- centralized governance across branches;
- branch-level reporting;
- cross-branch roster and inventory;
- future franchise isolation.

### 20. API-First and Integration Layer Need More Detail

The requirements mention API-first and future integrations. The source calls for:

- API gateway;
- OAuth2;
- rate limiting;
- webhook engine;
- developer portal;
- external APIs;
- accounting/payroll/banking/pharmacy/telehealth/Medicare readiness.

Gap: requirements should define integration boundaries and minimum API governance.

### 21. Healthcare Interoperability Is Present but Deferred

FHIR, HL7, SNOMED CT, and ICD-10 are present in future requirements. This aligns with the source. The gap is patient data boundary and architectural readiness: current MVP should avoid deep clinical scope while preserving identifiers and integration seams.

### 22. Offline Mode Is Correctly Mentioned but Conflicts With MVP Deferral

`docs/requirements.md` says offline continuity should support critical workflows where practical. `docs/phase-1/mvp-scope.md` defers offline-first mobile synchronization.

Gap: clarify the MVP target:

- no offline support;
- offline read-only task cache;
- offline capture with later sync;
- full offline-first sync.

### 23. Requirements Status Is Out of Date

`docs/requirements.md` says current phase is Phase 5. The repository README says the project is implemented through Phase 8.

Gap: update project status so product and implementation planning do not work from stale phase assumptions.

## Recommended Updates to `docs/requirements.md`

1. Add an "AHOS Operating Principles" section.
2. Expand Super Admin requirements with per-user task summaries, ticket drilldowns, appraisal/feedback, and task detail modal behavior.
3. Add a concrete AI actor taxonomy and AI action governance matrix.
4. Generalize barcode/QR requirements into a platform identity and workflow trigger system.
5. Add detailed contract, consent, and document lifecycle requirements.
6. Clarify payment readiness versus payment execution and tax/accounting boundaries.
7. Add event architecture and workflow/rule engine acceptance criteria.
8. Add role coverage for nurse, pharmacist, patient operational target, external accountant/lawyer, franchise partner, and non-human service entities.
9. Expand emergency, incident, visitor/access, and communication workflows.
10. Add architecture-facing future requirements for knowledge graph, digital twins, event sourcing, API gateway, webhooks, and zero trust controls.
11. Resolve the Phase 5 versus Phase 8 status mismatch.
12. Clarify which advanced source requirements are MVP, near-term, or future enterprise scope.

