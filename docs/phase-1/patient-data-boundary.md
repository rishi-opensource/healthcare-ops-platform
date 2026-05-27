# Patient Data Boundary

## MVP Position

The MVP is an operations platform, not an electronic health record. Patient support is limited to operational identifiers, appointment/ticket context, communication history, consent status, and incident linkage needed for clinic operations.

Clinical records, diagnosis, prescriptions, pathology, treatment plans, Medicare details, My Health Record data, and detailed health histories are out of scope unless explicitly approved in a later compliance phase.

## Patient Data Allowed in MVP

| Category | Allowed fields | Purpose |
|----------|----------------|---------|
| Patient reference | internal patient reference ID, display name, preferred contact label, status | Link tickets and communication to the right person |
| Contact metadata | phone/email presence flags, masked contact value, preferred channel | Send or record operational communication |
| Appointment reference | external appointment ID, appointment date/time, appointment type label, attendance state | Link reminders, missed appointments, and reception tasks |
| Consent status | consent type, version, status, signed/acknowledged timestamp, expiry if any | Prove consent workflow status |
| Communication log | channel, direction, timestamp, staff actor, summary, linked ticket | Operational traceability |
| Complaint/incident link | incident/ticket reference, category, status | Escalation and closure tracking |
| Check-in reference | QR/token identifier, check-in timestamp, location | Reception workflow support |

## Patient Data Excluded from MVP

- Diagnosis, clinical notes, treatment notes, and care plans.
- Prescription details beyond a non-clinical barcode or ticket reference.
- Medicare, insurance, payment card, or government identifier storage.
- My Health Record data.
- Pathology, imaging, observations, vitals, and test results.
- Detailed family history, allergies, medications, or condition lists.
- Full call transcripts unless approved by privacy review.
- Free-text patient health information in general ticket notes unless a later privacy design explicitly supports it.

## Privacy and Security Defaults

- Store the minimum patient data needed for the workflow.
- Prefer external patient IDs from an integrated source instead of duplicating clinical records.
- Mask patient contact details in list views by default.
- Require explicit role permissions for patient-linked detail views.
- Audit every patient-linked view and mutation once implementation supports read-audit for sensitive records.
- Keep patient communication summaries concise and operational.
- Attach patient records to tickets only when there is a business need.
- Make patient exports permission-scoped and auditable.
- Add retention/de-identification controls before production launch.

## Data Classification

| Classification | Examples | Controls |
|----------------|----------|----------|
| Public | none in patient context | Do not expose patient data publicly |
| Internal | appointment type label, ticket status | Authenticated role access |
| Sensitive | patient name, masked contact, communication summaries, consent status | Role-scoped access, audit, export limits |
| Restricted | privacy incidents, complaint details, emergency workflows | Compliance/manager access, stronger audit |
| Excluded | clinical notes, diagnosis, Medicare, My Health Record | Do not store in MVP |

## UI Rules

- Mobile task cards show patient initials or short display labels, not full sensitive details unless required.
- Web tables show masked contact and operational status only.
- Patient-linked ticket detail must visually mark sensitive context.
- Free-text inputs that may include patient information should include labels that ask for operational summaries only.
- Exports containing patient-linked records require elevated permission.

## API Rules

- Patient reference endpoints return DTOs with only permitted fields.
- Staff endpoints must be filtered by assigned ticket, branch, role, or explicit permission.
- Patient-linked search must require at least one useful filter, such as name, reference ID, appointment ID, ticket ID, or contact fragment.
- Patient-linked audit metadata must include actor, action, object type, object ID, branch, and request ID.

## Open Compliance Questions

- Which Australian privacy, healthcare, and record-retention obligations apply to Healthcare Doctors' exact services?
- Will the MVP integrate with a medical booking or clinical record system?
- Is SMS/email handled by the platform or an external communications system?
- Are call recordings/transcripts required for the AI receptionist?
- What is the approved retention period for patient communication logs and consent records?
