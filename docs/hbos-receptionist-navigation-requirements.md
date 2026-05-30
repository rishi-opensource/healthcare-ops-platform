# Healthcare HBOS Receptionist Navigation Requirements

Source of truth: Image #2, "Receptionist Navigation Journey on Mobile App".

Product name: Healthcare Business OS (HBOS), also referred to as Adaptive Healthcare Operating System (AHOS) in product visuals.

Primary persona: Receptionist, represented in the source visual as Emma Johnson, Receptionist, ID `REC-10045`, active.

## 1. Product Intent

Healthcare HBOS must provide a mobile-first receptionist workspace that supports the receptionist's complete operational journey from onboarding through daily work, inventory scanning, ticket creation, leave/roster communication, attendance, payroll approval, profile management, and help/support.

The mobile app must act as a single operational cockpit for the receptionist. It must reduce context switching, allow common workflows to be completed quickly, and preserve auditability for every important action.

The platform must be:

- AI powered.
- Voice enabled.
- Barcode enabled.
- Secure.
- Compliant.
- Mobile first.
- Web mirrored where supervisor/admin review is required.

## 2. Core Principles

1. Every operational activity should be traceable.
2. Every important action should create or link to a ticket where appropriate.
3. Every scanned barcode or QR code should resolve to a known entity, document, asset, patient, item, ticket, invoice, delivery, or workflow.
4. Every receptionist action should be role-scoped and audit logged.
5. Mobile workflows should be simple, fast, and task-oriented.
6. AI and voice workflows should assist the receptionist but must not bypass approval, compliance, or audit requirements.
7. Payroll readiness should be based on verified attendance, task completion, approvals, and manager review.

## 3. User Profile Requirements

The receptionist profile panel must show:

- Profile photo.
- Full name.
- Role.
- Staff/reference ID.
- Active/inactive status.
- Short role description.
- Permission summary.
- Voice and barcode assistant availability.

The source visual defines the receptionist responsibilities as:

- Front desk operations.
- Appointment management.
- Inventory support.
- Stock management.
- Roster and leave coordination.
- Patient communication.
- Team communication.
- Mobile workflow completion using voice and barcode assistant.

## 4. Journey Overview

The receptionist mobile journey must include five major workflow sections:

1. Onboarding Journey.
2. Daily Work Journey.
3. Inventory, Barcode, and Ticketing Workflow.
4. Leave, Roster, and Communication.
5. Attendance, Time Tracking, and Payroll.

The mobile app must expose the following high-level capabilities:

- Onboarding and registration.
- Profile completion.
- Document upload.
- Contract and policy signing.
- Training and orientation.
- Dashboard/home screen.
- Appointment management.
- Patient check-in.
- Tasks and to-do management.
- Messages.
- Voice assistant.
- Barcode/scan center.
- Quick actions.
- Inventory scan and stock operations.
- Ticket creation and ticket lifecycle tracking.
- Leave management.
- Roster viewing.
- Shift detail and shift swap/request.
- Team chat.
- Announcements.
- Clock in/out.
- Attendance calendar.
- Payslip view.
- Pay approval tracking.
- Profile management.
- Help and support.

## 5. Onboarding Journey Requirements

### 5.1 Invite and Register

The system must support invitation-based receptionist registration.

Required fields and behavior:

- The receptionist receives an email or SMS invite.
- The invite contains a secure registration link.
- The invite screen welcomes the user to Healthcare Doctors.
- The receptionist can accept the invite.
- Existing users can navigate to login.
- The invitation must be single-use or otherwise protected from unauthorized reuse.
- Invite acceptance must create an audit event.

Acceptance criteria:

- Given a valid invite, the receptionist can open the registration flow.
- Given an expired or invalid invite, the system shows a safe error and does not create an account.
- The system records who invited the receptionist and when the invite was accepted.

### 5.2 Profile Setup

The app must allow the receptionist to complete a profile.

Required profile fields:

- Full name.
- Phone number.
- Email address.
- Role.
- Department.

Required behavior:

- Profile fields should be prefilled where known.
- Required fields must be validated.
- Role and department assignment must be controlled by authorized admin/HR data.
- The receptionist can proceed only after required fields are complete.

### 5.3 Document Upload

The app must support onboarding document upload and status tracking.

Required document examples from the source visual:

- ID proof.
- Passport.
- Police check.
- Certificate or qualification document.

Required behavior:

- Each required document must show pending, uploaded, approved, rejected, or expired status.
- The receptionist can upload document evidence from mobile.
- Uploaded documents must be linked to the receptionist entity.
- Uploaded documents must be visible to HR/compliance reviewers on web.
- Document upload, review, rejection, and approval must create audit events.

### 5.4 Contract and Policy Review

The app must support mobile review and signing of employment documents.

Required documents:

- Employment contract.
- Privacy policy.
- Code of conduct.
- Other company policies assigned to the role.

Required behavior:

- The receptionist can view each document before signing.
- The receptionist can sign and continue.
- Signed documents must record signer, timestamp, version, and evidence.
- Policy acknowledgement must be versioned.
- Updated policy versions must be re-acknowledged.

### 5.5 Training and Orientation

The app must support training progress and compliance modules.

Required training examples:

- Introduction to AHOS/HBOS.
- Workplace safety.
- Privacy and compliance.
- System training.

Required behavior:

- Training progress must be visible as a percentage.
- Each training module must show completion status.
- Training may include learning content, quiz, or acknowledgement.
- Training completion must create a certificate/proof record where required.
- Required training must block onboarding completion until complete if configured.

### 5.6 Onboarding Complete

The app must show a completion screen after onboarding requirements are satisfied.

Required behavior:

- The user sees a completion confirmation.
- Access is granted according to assigned role permissions.
- The app offers navigation to the dashboard.
- Role permissions must be applied immediately after activation.
- Completion must create an audit event and update the onboarding workflow state.

## 6. Daily Work Journey Requirements

### 6.1 Dashboard / Home

The receptionist dashboard must summarize the day.

Required data:

- Greeting and user identity.
- Today's date or selected date.
- Today's summary.
- Number of patients.
- Number of open/pending tasks.
- Number of tasks or alerts.
- Today's schedule.
- Quick actions.

Required behavior:

- Dashboard cards must be tappable where detail records exist.
- Dashboard must update from backend data.
- Dashboard must show role-specific content.
- Critical alerts should be visually distinct.

### 6.2 Appointments

The app must support appointment viewing and appointment creation.

Required data:

- Appointment date.
- Appointment time.
- Patient name.
- Appointment type.
- Provider/doctor.
- Appointment status.

Required behavior:

- The receptionist can view today's appointments.
- The receptionist can filter appointments.
- The receptionist can add a new appointment.
- The receptionist can view, book, or modify appointment details subject to permission.
- Appointment actions should create or link to tickets where operational follow-up is needed.

### 6.3 Patient Check-In

The app must support patient check-in.

Required data:

- Patient name.
- Patient ID/reference.
- Appointment time.
- Verification steps.

Required check-in steps:

- Verify patient details.
- Check insurance or billing information where applicable.
- Confirm forms.
- Complete check-in.

Required behavior:

- The receptionist can check in a patient from mobile.
- Missing forms or failed verification should create an alert or ticket.
- Check-in must be audit logged.
- Patient data shown on mobile must follow the approved patient data boundary.

### 6.4 Tasks and To-Do

The app must support assigned receptionist tasks.

Required views:

- Pending tasks.
- Completed tasks.
- Task detail.

Required task examples:

- Send reports.
- Prepare room.
- Follow up call.
- Update patient file.

Required behavior:

- Tasks must show status, priority, and assignment.
- The receptionist can start, update, and complete tasks.
- Completed tasks must capture a completion summary or evidence where required.
- Task completion can request manager approval.
- Tasks should be linked to ticket numbers.

### 6.5 Messages

The app must support internal messages and department updates.

Required message categories:

- Doctor or provider messages.
- Nurse station messages.
- Pharmacy messages.
- Admin team messages.
- Department updates.

Required behavior:

- The receptionist can view messages.
- The receptionist can send new messages.
- Messages can be linked to tickets or patient/appointment context where permitted.
- Sensitive communication must be audit logged and access controlled.

### 6.6 Voice Assistant

The app must provide a voice assistant for hands-free operations.

Required example commands:

- "Book appointment for John at 10 AM."
- "Check stock of surgical masks."
- "Show my roster for this week."
- "Apply leave for next Monday."
- "Raise ticket for low stock."
- "Send message to Nurse Station."
- "Show today's appointments."

Required behavior:

- Voice commands must be transcribed.
- The user must confirm high-impact actions before submission.
- Voice actions must keep transcript, confidence score, command intent, created records, and audit history.
- Failed or ambiguous voice commands must ask for clarification.
- Voice assistant must respect role permissions.

### 6.7 Barcode / Scan Center

The app must provide a scan center for barcode and QR workflows.

Required scan shortcuts:

- Scan barcode.
- Scan QR code.
- Scan patient.
- Manual entry.

Required behavior:

- Scans must resolve to known records when possible.
- Unknown scans should offer safe next actions, such as create item, create ticket, or report issue.
- Scan results must support context-specific actions.
- Scan actions must be logged where they change operational state.

### 6.8 Quick Actions

The app must provide one-tap actions.

Required quick actions:

- Add patient.
- New appointment.
- Issue invoice.
- Collect payment.
- Create ticket.
- Check stock.

Required behavior:

- Quick actions must be role-scoped.
- Actions that create or mutate records must be confirmed where appropriate.
- Quick actions must save time but must not bypass compliance controls.

## 7. Inventory, Barcode, and Ticketing Requirements

### 7.1 Scan Item

The receptionist must be able to scan an item barcode using mobile camera or scanner.

Required behavior:

- Camera scanner opens from scan center.
- Barcode frame or guide is shown.
- Scanned value resolves to item details.
- Scan failures allow retry or manual entry.

### 7.2 Item Details

The item details screen must show:

- Item name.
- SKU or product code.
- Category.
- Current stock.
- Unit.
- Location.
- Expiry date where applicable.
- Batch details where applicable.

### 7.3 Stock Actions

The app must support stock operations.

Required stock actions:

- Stock in.
- Stock out.
- Transfer.
- Adjust stock.
- Return.
- View history.

Required behavior:

- Each stock action must record quantity, user, timestamp, location, and reason.
- Stock action permissions must be role-scoped.
- Material stock changes must be auditable.

### 7.4 Scan for Stock In

The app must support scanning supplier/item barcode during stock-in.

Required behavior:

- User scans supplier/item barcode.
- App identifies item and batch where possible.
- User enters quantity and confirms.
- Stock levels update in real time.

### 7.5 Enter Quantity

The stock-in screen must capture:

- Item.
- Quantity.
- Unit.
- Batch number.
- Expiry date.
- Location.

Validation:

- Quantity must be positive.
- Expiry date must be valid where required.
- Batch number must be required for batch-tracked items.

### 7.6 Stock Updated

The app must show stock update confirmation.

Required behavior:

- Confirmation screen shows success state.
- New stock count is visible.
- User can view stock details after update.
- Stock update must create inventory movement history.

### 7.7 Create Ticket

The app must support automatic or manual ticket creation from inventory events.

Required inventory ticket examples:

- Low stock alert.
- Damaged item.
- Missing item.
- Expiring batch.
- Delivery mismatch.
- Stock adjustment review.

Required create ticket fields:

- Issue type.
- Item.
- Priority.
- Description.
- Related barcode/item/batch.

### 7.8 Ticket Created

The app must show ticket creation confirmation.

Required ticket data:

- Ticket number.
- Ticket title.
- Status.
- Priority.
- Created date/time.
- Assigned owner or queue.

Required behavior:

- User can open the ticket from confirmation screen.
- Ticket appears in the relevant task/ticket list.
- Ticket lifecycle status is trackable.

### 7.9 Barcode Applications Across HBOS

The system must support barcode/QR usage for:

- Patient wristband: patient check-in and info lookup.
- Medicine/product: verify medicine, expiry, and batch.
- Asset tracking: track equipment and devices.
- Documents: scan and upload documents.
- ID cards: verify staff or visitor identification.
- Invoices: scan invoice for processing.
- Delivery/GRN: scan goods receipt note and items.
- Ticket QR: open and track ticket workflow.

### 7.10 Ticket Lifecycle

Ticket lifecycle must support:

- Open.
- Assigned.
- In progress.
- Resolved.
- Closed.

The lifecycle must preserve:

- Creator.
- Assignee.
- Status history.
- Notes.
- Evidence.
- Approvals.
- Audit log.

## 8. Leave, Roster, and Communication Requirements

### 8.1 Leave Management

The app must show leave balances.

Required leave types:

- Annual leave.
- Sick leave.
- Personal leave.

Required behavior:

- User can view leave balance.
- User can apply leave.
- User can view past and pending leave requests.
- Leave requests must route through approval workflow.

### 8.2 Apply Leave

Required leave application fields:

- Leave type.
- Start date.
- End date.
- Reason.

Required behavior:

- User submits leave request.
- Manager receives approval task.
- User can track approval status.
- Approved leave updates roster/workforce views.

### 8.3 Roster View

The app must show roster calendar.

Required data:

- Month/week view.
- Shift dates.
- Shift times.
- Role or position.
- Location/branch.

Required behavior:

- User can view roster.
- User can identify upcoming shifts.
- User can view shift details.

### 8.4 Shift Details

The app must show:

- Shift date.
- Shift start/end time.
- Role.
- Branch/location.
- Break time.
- Team or department.

Required behavior:

- User can request shift swap where allowed.
- Shift swap/request must create an approval workflow.

### 8.5 Team Chat

The app must support team communication.

Required behavior:

- User can read team chat.
- User can send messages.
- Chat must support real-time or near-real-time updates.
- Messages must be role/department scoped.

### 8.6 Announcements

The app must show company announcements.

Required announcement examples:

- System updates.
- Holiday notices.
- Staff meeting notices.
- Training session notices.

Required behavior:

- Announcements must show title, summary, timestamp, and source.
- Important announcements can require acknowledgement.

## 9. Attendance, Time Tracking, and Payroll Requirements

### 9.1 Attendance / Clock In

The app must support shift clock in/out.

Required data:

- Working timer.
- Start time.
- Break duration.
- Shift date.
- End shift action.

Required behavior:

- User can clock in.
- User can clock out/end shift.
- User can record breaks where required.
- Attendance records must link to rostered shift where possible.
- Clock actions must create audit events.

### 9.2 Attendance Calendar

The app must show attendance history.

Required data:

- Calendar view.
- Present days.
- Absent days.
- Late days.
- Attendance summary.
- History and reports.

Required behavior:

- User can review attendance records.
- Exceptions must be visible.
- Managers must be able to review attendance exceptions on web.

### 9.3 Payslip

The app must show payslip details when available.

Required payslip data:

- Pay period.
- Net pay.
- Gross pay.
- Tax.
- Deductions.

Required behavior:

- User can view payslip.
- User can download or access pay slip where permitted.
- Payslip data may be imported from payroll system or generated as readiness data depending on integration phase.

### 9.4 Pay Approval

The app must show pay approval status.

Required data:

- Approval status.
- Approver.
- Approval date.
- Payment date.
- Payment certification/confirmation message.

Required behavior:

- User can track payment approval.
- Manager/admin approval must happen in authorized web/admin workflow.
- The app must distinguish payroll readiness from actual payment execution if payment execution is not in scope.

### 9.5 Profile

The app must support profile management.

Required profile options:

- My profile.
- Change password.
- Notification settings.
- App settings.
- Help and support.
- Logout.

Required behavior:

- Sensitive profile changes must require re-authentication where needed.
- Password changes must follow security policy.

### 9.6 Help and Support

The app must provide support access.

Required help options:

- FAQ.
- Raise support ticket.
- Call support.
- Live chat.

Required behavior:

- User can search help content.
- User can raise a support ticket from mobile.
- Support tickets must be traceable.

## 10. Security and Compliance Requirements

The platform must support:

- End-to-end encryption where appropriate.
- Role-based access control.
- Audit logs for every important action.
- Compliance with Australian Privacy Principles (APP).
- Secure authentication.
- Session protection.
- Permission-scoped mobile screens.
- Privacy-safe patient data display.

Security requirements:

- Staff must authenticate before accessing app data.
- Sensitive actions should require confirmation.
- Lost or inactive users must have access revocation.
- All contract signing, document upload, training completion, check-in, inventory update, ticket creation, attendance, and payroll-readiness actions must be auditable.

## 11. Mobile UX Requirements

The app must be optimized for mobile receptionist workflows.

UX requirements:

- Clear section-based navigation.
- Large touch targets.
- Fast access to voice and scan actions.
- Quick action menu.
- Status badges for active, pending, approved, urgent, and completed states.
- Confirmation screens after high-value actions.
- Error states that explain what went wrong and what to do next.
- Loading states for remote data.
- Accessible text contrast.
- Simple language suitable for busy front desk users.

## 12. Web Mirroring Requirements

Although Image #2 focuses on mobile, supervisor and admin workflows must be mirrored or reviewable on web.

Web users must be able to review:

- Onboarding progress.
- Uploaded documents.
- Contract and policy status.
- Training completion.
- Appointment/check-in exceptions.
- Task and ticket completion.
- Inventory movements.
- Ticket lifecycle.
- Leave approvals.
- Roster and shift requests.
- Attendance exceptions.
- Payroll readiness.
- Support tickets.
- Audit logs.

## 13. MVP Requirements

The MVP should include:

1. Mobile login and invite acceptance.
2. Profile completion.
3. Document upload/status.
4. Contract/policy acknowledgement.
5. Training progress and completion.
6. Daily dashboard.
7. Assigned tasks and ticket completion.
8. Barcode scan center and barcode resolution.
9. Inventory item lookup and stock-in/stock-out.
10. Inventory ticket creation for low stock.
11. Leave balance and leave request.
12. Roster view and shift detail.
13. Clock in/out and attendance history.
14. Payroll readiness status.
15. Profile/settings.
16. Help/support ticket creation.
17. Audit logging for all important actions.

## 14. Near-Term Requirements

Near-term post-MVP should include:

- Appointment creation and modification.
- Patient check-in with verification.
- Team chat.
- Announcements with acknowledgement.
- Voice assistant command execution.
- Payslip view/download.
- Shift swap/request.
- Delivery/GRN barcode workflows.
- Invoice barcode workflows.
- Document barcode workflows.
- Ticket QR workflow.

## 15. Future Enterprise Requirements

Future enterprise scope should include:

- Voice biometric login.
- Multi-language voice assistant.
- Real-time team chat.
- Offline capture and later sync.
- Advanced appointment integrations.
- Payroll/payment execution integrations.
- Accounting and BAS/GST integrations.
- Patient wristband scanning.
- Medicine/prescription barcode verification.
- Visitor badge QR workflow.
- Advanced AI assistant for policy and workflow guidance.
- Predictive stock and workforce alerts.
- Multi-branch roster and inventory balancing.

## 16. Acceptance Checklist Against Image #2

The product is aligned with Image #2 when all of the following are true:

- Receptionist can complete onboarding from invite to dashboard access.
- Receptionist can complete profile, upload documents, sign policies, and finish training.
- Receptionist sees a daily dashboard with tasks, appointments, schedule, and quick actions.
- Receptionist can manage appointments and patient check-in.
- Receptionist can view, update, and complete tasks.
- Receptionist can use voice assistant for supported commands.
- Receptionist can scan barcodes/QR codes and perform context-specific actions.
- Receptionist can perform inventory stock actions and create low-stock tickets.
- Receptionist can track ticket lifecycle.
- Receptionist can view leave balance and apply leave.
- Receptionist can view roster and shift details.
- Receptionist can use team chat and view announcements.
- Receptionist can clock in/out and review attendance.
- Receptionist can view payslip/pay approval status.
- Receptionist can manage profile and request support.
- All important actions are secure, compliant, permission-scoped, and audit logged.

