export type RoleAssignment = {
  id: number;
  role_code: string;
  role_name: string;
  branch_name?: string | null;
};

export type CurrentUser = {
  id: number;
  email: string;
  full_name: string;
  primary_branch_name?: string | null;
  roles: RoleAssignment[];
};

export type LoginResponse = {
  token: string;
  user: CurrentUser;
};

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export type DashboardMetric = {
  label: string;
  value: string;
  href: string;
  tone: "info" | "warning" | "danger" | "success" | "neutral";
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type TicketStatus =
  | "draft"
  | "open"
  | "in_progress"
  | "waiting_approval"
  | "needs_correction"
  | "completed"
  | "closed"
  | "cancelled";

export type TicketPriority = "low" | "normal" | "high" | "urgent";

export type TicketCategory =
  | "general"
  | "onboarding"
  | "patient"
  | "appointment"
  | "inventory"
  | "purchase_order"
  | "payroll"
  | "leave"
  | "incident"
  | "contract"
  | "ai_created"
  | "supplier"
  | "maintenance";

export type TicketListItem = {
  id: number;
  ticket_number: string;
  category: TicketCategory;
  title: string;
  status: TicketStatus;
  priority: TicketPriority;
  due_at: string | null;
  branch: number | null;
  branch_name: string | null;
  created_by_email: string | null;
  assigned_to: number | null;
  assigned_to_email: string | null;
  pending_approval_count: number;
  created_at: string;
  updated_at: string;
};

export type TicketComment = {
  id: number;
  author: number | null;
  author_email: string | null;
  body: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
};

export type TicketStatusHistory = {
  id: number;
  from_status: string;
  to_status: TicketStatus;
  changed_by: number | null;
  changed_by_email: string | null;
  note: string;
  created_at: string;
};

export type TicketApproval = {
  id: number;
  approval_type: string;
  status: "pending" | "approved" | "rejected" | "correction_requested";
  requested_by: number | null;
  requested_by_email: string | null;
  reviewed_by: number | null;
  reviewed_by_email: string | null;
  reviewed_at: string | null;
  decision_note: string;
  created_at: string;
  updated_at: string;
};

export type TaskCompletion = {
  id: number;
  completed_by: number | null;
  completed_by_email: string | null;
  task_name: string;
  task_category: string;
  time_spent_minutes: number;
  outcome: string;
  payroll_link_approved: boolean;
  appraisal_rating: number | null;
  appraisal_comments: string;
  created_at: string;
  updated_at: string;
};

export type Ticket = TicketListItem & {
  description: string;
  created_by: number | null;
  related_entity: number | null;
  related_entity_name: string | null;
  source: "web" | "mobile" | "admin" | "ai" | "system";
  completion_summary: string;
  completed_at: string | null;
  metadata: Record<string, unknown>;
  status_history: TicketStatusHistory[];
  comments: TicketComment[];
  approvals: TicketApproval[];
  task_completion: TaskCompletion | null;
};

export type TicketSummary = {
  open: number;
  in_progress: number;
  waiting_approval: number;
  needs_correction: number;
  completed: number;
  urgent: number;
  assigned_to_me: number;
};

export type Branch = {
  id: number;
  organization: number;
  organization_name: string;
  name: string;
  code: string;
};

export type UserListItem = {
  id: number;
  email: string;
  full_name: string;
  primary_branch: number | null;
  primary_branch_name: string | null;
};

export type CreateTicketInput = {
  title: string;
  description?: string;
  category?: TicketCategory;
  priority?: TicketPriority;
  branch?: number | null;
  assigned_to?: number | null;
  due_at?: string | null;
  source?: "web" | "mobile";
};

export type EntityType =
  | "employee"
  | "doctor"
  | "contractor"
  | "supplier"
  | "patient_reference"
  | "ai_agent"
  | "inventory_item"
  | "medicine"
  | "equipment"
  | "device"
  | "room"
  | "branch"
  | "contract"
  | "service"
  | "digital_asset";

export type EntityStatus = "draft" | "onboarding" | "active" | "suspended" | "archived";
export type OnboardingStatus = "not_started" | "in_progress" | "waiting_approval" | "completed" | "cancelled";
export type OnboardingStepStatus = "pending" | "completed" | "verified" | "needs_correction" | "waived";

export type EntityListItem = {
  id: number;
  entity_type: EntityType;
  display_name: string;
  status: EntityStatus;
  branch: number | null;
  branch_name: string | null;
  responsible_user: number | null;
  responsible_email: string | null;
  external_reference: string;
  qr_code_value: string | null;
  onboarding_status: OnboardingStatus | null;
  completed_step_count: number;
  required_step_count: number;
  created_at: string;
  updated_at: string;
};

export type OnboardingStepCompletion = {
  id: number;
  name: string;
  step_type: string;
  status: OnboardingStepStatus;
  related_ticket: number | null;
  related_ticket_number: string | null;
  document_assignment: number | null;
  document_template_name: string | null;
  completed_at: string | null;
  verified_at: string | null;
  note: string;
  evidence_label: string;
};

export type EntityOnboarding = {
  id: number;
  workflow_template: number | null;
  workflow_template_name: string | null;
  status: OnboardingStatus;
  activation_ticket: number | null;
  activation_ticket_number: string | null;
  required_step_count: number;
  completed_step_count: number;
  step_completions: OnboardingStepCompletion[];
};

export type Entity = EntityListItem & {
  owner_user: number | null;
  owner_email: string | null;
  metadata: Record<string, unknown>;
  onboarding: EntityOnboarding | null;
  lifecycle_events: Array<{
    id: number;
    from_status: string;
    to_status: EntityStatus;
    changed_by_email: string | null;
    note: string;
    created_at: string;
  }>;
};

export type CreateEntityInput = {
  entity_type: EntityType;
  display_name: string;
  status?: EntityStatus;
  branch?: number | null;
  owner_user?: number | null;
  responsible_user?: number | null;
  external_reference?: string;
  qr_code_value?: string | null;
  metadata?: Record<string, unknown>;
  profile?: Record<string, unknown>;
};

export type EntitySummary = {
  draft: number;
  onboarding: number;
  active: number;
  suspended: number;
  archived: number;
  waiting_approval: number;
  pending_steps: number;
};

export type OnboardingWorkflowTemplate = {
  id: number;
  entity_type: EntityType;
  name: string;
  description: string;
  is_active: boolean;
  step_count: number;
};

export type DocumentAssignmentStatus = "assigned" | "viewed" | "acknowledged" | "signed" | "expired" | "cancelled";

export type DocumentAssignment = {
  id: number;
  template: number;
  template_name: string;
  template_type: string;
  assigned_to_user: number | null;
  assigned_to_email: string | null;
  assigned_to_entity: number | null;
  assigned_to_entity_name: string | null;
  assigned_by: number | null;
  assigned_by_email: string | null;
  status: DocumentAssignmentStatus;
  due_at: string | null;
  completed_at: string | null;
  version: string;
  acknowledgement_text: string;
  evidence_label: string;
  expires_at: string | null;
  renewal_ticket: number | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ConsentRecordStatus = "given" | "withdrawn" | "expired";

export type ConsentRecord = {
  id: number;
  consent_type: string;
  subject_user: number | null;
  subject_user_email: string | null;
  subject_entity: number | null;
  subject_entity_name: string | null;
  document_assignment: number | null;
  status: ConsentRecordStatus;
  purpose: string;
  scope: string;
  granted_by: number | null;
  granted_by_email: string | null;
  granted_at: string | null;
  withdrawn_at: string | null;
  expires_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type TrainingModule = {
  id: number;
  title: string;
  module_type: string;
  description: string;
  version: string;
  validity_days: number;
  quiz_required: boolean;
  certificate_required: boolean;
  is_active: boolean;
  assignment_count: number;
  created_at: string;
  updated_at: string;
};

export type TrainingAssignmentStatus = "assigned" | "in_progress" | "completed" | "overdue" | "expired" | "waived";

export type TrainingAssignment = {
  id: number;
  module: number;
  module_title: string;
  module_type: string;
  assigned_to_user: number | null;
  assigned_to_email: string | null;
  assigned_to_entity: number | null;
  assigned_to_entity_name: string | null;
  assigned_by: number | null;
  assigned_by_email: string | null;
  status: TrainingAssignmentStatus;
  due_at: string | null;
  completed_at: string | null;
  expires_at: string | null;
  reviewed_by: number | null;
  reviewed_by_email: string | null;
  reviewed_at: string | null;
  completion_note: string;
  quiz_score: number | null;
  certificate_label: string;
  evidence_label: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ComplianceSummary = {
  assigned_documents: number;
  pending_documents: number;
  signed_documents: number;
  expiring_documents: number;
  active_consents: number;
  expired_consents: number;
  assigned_training: number;
  completed_training: number;
  overdue_training: number;
  expiring_training: number;
};

export type DashboardReport = {
  generated_at: string;
  scope: string;
  tickets: {
    open: number;
    in_progress: number;
    waiting_approval: number;
    needs_correction: number;
    completed: number;
    overdue: number;
    urgent: number;
    pending_approvals: number;
  };
  entities: {
    active: number;
    onboarding: number;
    pending_onboarding_steps: number;
    waiting_onboarding_approval: number;
  };
  workforce: {
    users_working: number;
    completed_tasks: number;
    payroll_ready: number;
    appraisal_feedback_pending: number;
  };
  operations: {
    payroll_pending: number;
    leave_pending: number;
    inventory_alerts: number;
    incidents_open: number;
    ai_review_pending: number;
  };
  compliance: {
    pending_documents: number;
    signed_documents: number;
    expiring_documents: number;
    active_consents: number;
    overdue_training: number;
    expiring_training: number;
  };
  daily_workspace: {
    due_today: number;
    handover: number;
    stock_warnings: number;
    pending_approvals: number;
    communication_followups: number;
  };
};

export type UserTaskSummary = {
  user_id: number | null;
  email: string | null;
  full_name: string | null;
  completed_tasks: number;
  total_minutes: number;
  payroll_ready: number;
  correction_requests: number;
  appraisal_feedback: number;
};

export type ReportExport = {
  report_type: string;
  generated_at: string;
  rows: Array<Record<string, unknown>>;
};

export type ShiftStatus = "draft" | "published" | "completed" | "cancelled";
export type LeaveRequestStatus = "requested" | "approved" | "rejected" | "cancelled";
export type AttendanceStatus = "clocked_in" | "clocked_out" | "exception";
export type HandoverStatus = "open" | "acknowledged" | "closed";
export type TimesheetStatus = "draft" | "submitted" | "approved" | "needs_correction";

export type Shift = {
  id: number;
  branch: number;
  branch_name: string;
  staff_user: number;
  staff_email: string;
  role_label: string;
  starts_at: string;
  ends_at: string;
  status: ShiftStatus;
  notes: string;
  overtime_minutes: number;
  published_by: number | null;
  published_by_email: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

export type LeaveRequest = {
  id: number;
  staff_user: number;
  staff_email: string;
  branch: number | null;
  branch_name: string | null;
  leave_type: string;
  starts_at: string;
  ends_at: string;
  reason: string;
  status: LeaveRequestStatus;
  reviewed_by: number | null;
  reviewed_by_email: string | null;
  reviewed_at: string | null;
  review_note: string;
  related_ticket: number | null;
  related_ticket_number: string | null;
  created_at: string;
  updated_at: string;
};

export type AttendanceRecord = {
  id: number;
  staff_user: number;
  staff_email: string;
  shift: number | null;
  shift_label: string;
  branch: number | null;
  branch_name: string | null;
  clock_in_at: string;
  clock_out_at: string | null;
  status: AttendanceStatus;
  exception_note: string;
  location_label: string;
  approved_by: number | null;
  approved_by_email: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
};

export type HandoverNote = {
  id: number;
  branch: number;
  branch_name: string;
  author: number | null;
  author_email: string | null;
  assigned_to: number | null;
  assigned_to_email: string | null;
  title: string;
  body: string;
  status: HandoverStatus;
  due_at: string | null;
  acknowledged_by: number | null;
  acknowledged_by_email: string | null;
  acknowledged_at: string | null;
  created_at: string;
  updated_at: string;
};

export type TimesheetSummary = {
  id: number;
  staff_user: number;
  staff_email: string;
  branch: number | null;
  branch_name: string | null;
  period_start: string;
  period_end: string;
  scheduled_minutes: number;
  worked_minutes: number;
  task_minutes: number;
  exception_count: number;
  payroll_ready: boolean;
  status: TimesheetStatus;
  submitted_at: string | null;
  reviewed_by: number | null;
  reviewed_by_email: string | null;
  reviewed_at: string | null;
  review_note: string;
  created_at: string;
  updated_at: string;
};

export type WorkforceSummary = {
  published_shifts: number;
  open_leave_requests: number;
  clocked_in: number;
  attendance_exceptions: number;
  open_handovers: number;
  payroll_ready: number;
  timesheets_needing_review: number;
};

export type StockItemStatus = "active" | "low_stock" | "archived";
export type StockMovementType = "receipt" | "issue" | "adjustment" | "damage" | "transfer";
export type PurchaseOrderStatus = "draft" | "ordered" | "part_received" | "received" | "cancelled";

export type StockItem = {
  id: number;
  entity: number | null;
  entity_name: string | null;
  branch: number;
  branch_name: string;
  name: string;
  sku: string;
  barcode: string;
  unit: string;
  quantity_on_hand: number;
  reorder_threshold: number;
  status: StockItemStatus;
  preferred_supplier: number | null;
  preferred_supplier_name: string | null;
  created_at: string;
  updated_at: string;
};

export type InventoryBatch = {
  id: number;
  stock_item: number;
  stock_item_name: string;
  batch_number: string;
  expiry_date: string | null;
  quantity: number;
  location_label: string;
  created_at: string;
  updated_at: string;
};

export type StockMovement = {
  id: number;
  stock_item: number;
  stock_item_name: string;
  batch: number | null;
  batch_number: string | null;
  movement_type: StockMovementType;
  quantity_delta: number;
  note: string;
  performed_by: number | null;
  performed_by_email: string | null;
  related_ticket: number | null;
  related_ticket_number: string | null;
  created_at: string;
  updated_at: string;
};

export type PurchaseOrderLine = {
  id: number;
  stock_item: number;
  stock_item_name: string;
  quantity_ordered: number;
  quantity_received: number;
};

export type PurchaseOrder = {
  id: number;
  branch: number;
  branch_name: string;
  supplier: number | null;
  supplier_name: string | null;
  po_number: string;
  status: PurchaseOrderStatus;
  requested_by: number | null;
  requested_by_email: string | null;
  ordered_at: string | null;
  expected_at: string | null;
  notes: string;
  lines: PurchaseOrderLine[];
  created_at: string;
  updated_at: string;
};

export type DeliveryReceipt = {
  id: number;
  purchase_order: number | null;
  purchase_order_number: string | null;
  stock_item: number;
  stock_item_name: string;
  batch: number | null;
  batch_number: string | null;
  quantity_received: number;
  received_by: number | null;
  received_by_email: string | null;
  supplier_issue: string;
  damage_quantity: number;
  created_at: string;
  updated_at: string;
};

export type BarcodeResolution = {
  barcode: string;
  target_type: string;
  target_id: number | null;
  label: string;
};

export type InventorySummary = {
  stock_items: number;
  low_stock_items: number;
  expiring_batches: number;
  open_purchase_orders: number;
  damaged_deliveries: number;
  reorder_tickets: number;
};

export class ApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly getToken?: () => string | null | undefined
  ) {}

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/api/v1/health/", { auth: false });
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    return this.request<LoginResponse>("/api/v1/auth/login/", {
      auth: false,
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  }

  async me(): Promise<CurrentUser> {
    return this.request<CurrentUser>("/api/v1/auth/me/");
  }

  async listTickets(params: Record<string, string | number | undefined> = {}): Promise<PaginatedResponse<TicketListItem>> {
    return this.request<PaginatedResponse<TicketListItem>>(`/api/v1/tickets/${this.query(params)}`);
  }

  async ticketSummary(): Promise<TicketSummary> {
    return this.request<TicketSummary>("/api/v1/tickets/summary/");
  }

  async getTicket(id: number): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/`);
  }

  async createTicket(input: CreateTicketInput): Promise<Ticket> {
    return this.request<Ticket>("/api/v1/tickets/", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async transitionTicket(id: number, status: TicketStatus, note = ""): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/transition/`, {
      method: "POST",
      body: JSON.stringify({ status, note })
    });
  }

  async assignTicket(id: number, assigned_to: number | null, note = ""): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/assign/`, {
      method: "POST",
      body: JSON.stringify({ assigned_to, note })
    });
  }

  async addTicketComment(id: number, body: string, is_internal = true): Promise<TicketComment> {
    return this.request<TicketComment>(`/api/v1/tickets/${id}/comments/`, {
      method: "POST",
      body: JSON.stringify({ body, is_internal })
    });
  }

  async completeTicket(
    id: number,
    input: {
      completion_summary: string;
      task_name?: string;
      task_category?: string;
      time_spent_minutes?: number;
      outcome?: string;
      request_approval?: boolean;
    }
  ): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/complete/`, {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async reviewTicketApproval(
    ticketId: number,
    approvalId: number,
    status: TicketApproval["status"],
    decision_note = ""
  ): Promise<TicketApproval> {
    return this.request<TicketApproval>(`/api/v1/tickets/${ticketId}/approvals/${approvalId}/review/`, {
      method: "POST",
      body: JSON.stringify({ status, decision_note })
    });
  }

  async appraiseTicket(id: number, appraisal_rating: number, appraisal_comments = ""): Promise<TaskCompletion> {
    return this.request<TaskCompletion>(`/api/v1/tickets/${id}/appraisal/`, {
      method: "POST",
      body: JSON.stringify({ appraisal_rating, appraisal_comments })
    });
  }

  async approvePayrollLink(id: number, approved = true, note = ""): Promise<TaskCompletion> {
    return this.request<TaskCompletion>(`/api/v1/tickets/${id}/approve-payroll-link/`, {
      method: "POST",
      body: JSON.stringify({ approved, note })
    });
  }

  async requestTicketCorrection(id: number, note: string): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/request-correction/`, {
      method: "POST",
      body: JSON.stringify({ note })
    });
  }

  async taskSummary(): Promise<UserTaskSummary[]> {
    return this.request<UserTaskSummary[]>("/api/v1/tickets/task-summary/");
  }

  async dashboardReport(): Promise<DashboardReport> {
    return this.request<DashboardReport>("/api/v1/reports/dashboard/");
  }

  async userTaskSummary(): Promise<UserTaskSummary[]> {
    return this.request<UserTaskSummary[]>("/api/v1/reports/user-task-summary/");
  }

  async exportReport(type = "ticket_status"): Promise<ReportExport> {
    return this.request<ReportExport>(`/api/v1/reports/export/${this.query({ type })}`);
  }

  async listShifts(params: Record<string, string | number | undefined> = {}): Promise<PaginatedResponse<Shift>> {
    return this.request<PaginatedResponse<Shift>>(`/api/v1/shifts/${this.query(params)}`);
  }

  async publishShift(id: number): Promise<Shift> {
    return this.request<Shift>(`/api/v1/shifts/${id}/publish/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listLeaveRequests(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<LeaveRequest>> {
    return this.request<PaginatedResponse<LeaveRequest>>(`/api/v1/leave-requests/${this.query(params)}`);
  }

  async reviewLeaveRequest(id: number, status: LeaveRequestStatus, note = ""): Promise<LeaveRequest> {
    return this.request<LeaveRequest>(`/api/v1/leave-requests/${id}/review/`, {
      method: "POST",
      body: JSON.stringify({ status, note })
    });
  }

  async listAttendanceRecords(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<AttendanceRecord>> {
    return this.request<PaginatedResponse<AttendanceRecord>>(`/api/v1/attendance-records/${this.query(params)}`);
  }

  async clockIn(input: { shift?: number | null; location_label?: string } = {}): Promise<AttendanceRecord> {
    return this.request<AttendanceRecord>("/api/v1/attendance-records/clock-in/", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async clockOut(id: number, exception_note = ""): Promise<AttendanceRecord> {
    return this.request<AttendanceRecord>(`/api/v1/attendance-records/${id}/clock-out/`, {
      method: "POST",
      body: JSON.stringify({ exception_note })
    });
  }

  async approveAttendance(id: number): Promise<AttendanceRecord> {
    return this.request<AttendanceRecord>(`/api/v1/attendance-records/${id}/approve/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listHandoverNotes(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<HandoverNote>> {
    return this.request<PaginatedResponse<HandoverNote>>(`/api/v1/handover-notes/${this.query(params)}`);
  }

  async acknowledgeHandover(id: number): Promise<HandoverNote> {
    return this.request<HandoverNote>(`/api/v1/handover-notes/${id}/acknowledge/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listTimesheetSummaries(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<TimesheetSummary>> {
    return this.request<PaginatedResponse<TimesheetSummary>>(`/api/v1/timesheet-summaries/${this.query(params)}`);
  }

  async refreshTimesheet(input: {
    staff_user?: number | null;
    period_start?: string;
    period_end?: string;
  } = {}): Promise<TimesheetSummary> {
    return this.request<TimesheetSummary>("/api/v1/timesheet-summaries/refresh/", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async submitTimesheet(id: number): Promise<TimesheetSummary> {
    return this.request<TimesheetSummary>(`/api/v1/timesheet-summaries/${id}/submit/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async reviewTimesheet(id: number, status: TimesheetStatus, note = ""): Promise<TimesheetSummary> {
    return this.request<TimesheetSummary>(`/api/v1/timesheet-summaries/${id}/review/`, {
      method: "POST",
      body: JSON.stringify({ status, note })
    });
  }

  async workforceSummary(): Promise<WorkforceSummary> {
    return this.request<WorkforceSummary>("/api/v1/timesheet-summaries/summary/");
  }

  async listStockItems(params: Record<string, string | number | undefined> = {}): Promise<PaginatedResponse<StockItem>> {
    return this.request<PaginatedResponse<StockItem>>(`/api/v1/stock-items/${this.query(params)}`);
  }

  async moveStock(
    id: number,
    input: { movement_type: StockMovementType; quantity_delta: number; batch?: number | null; note?: string }
  ): Promise<StockMovement> {
    return this.request<StockMovement>(`/api/v1/stock-items/${id}/move/`, {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async createReorderTicket(id: number): Promise<{ ticket_id: number; ticket_number: string }> {
    return this.request<{ ticket_id: number; ticket_number: string }>(`/api/v1/stock-items/${id}/create-reorder-ticket/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listInventoryBatches(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<InventoryBatch>> {
    return this.request<PaginatedResponse<InventoryBatch>>(`/api/v1/inventory-batches/${this.query(params)}`);
  }

  async listPurchaseOrders(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<PurchaseOrder>> {
    return this.request<PaginatedResponse<PurchaseOrder>>(`/api/v1/purchase-orders/${this.query(params)}`);
  }

  async orderPurchaseOrder(id: number): Promise<PurchaseOrder> {
    return this.request<PurchaseOrder>(`/api/v1/purchase-orders/${id}/order/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listDeliveryReceipts(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<DeliveryReceipt>> {
    return this.request<PaginatedResponse<DeliveryReceipt>>(`/api/v1/delivery-receipts/${this.query(params)}`);
  }

  async receiveDelivery(input: {
    stock_item: number;
    purchase_order?: number | null;
    quantity_received: number;
    batch_number?: string;
    expiry_date?: string | null;
    supplier_issue?: string;
    damage_quantity?: number;
  }): Promise<DeliveryReceipt> {
    return this.request<DeliveryReceipt>("/api/v1/delivery-receipts/receive/", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async resolveBarcode(barcode: string): Promise<BarcodeResolution> {
    return this.request<BarcodeResolution>("/api/v1/barcode-aliases/resolve/", {
      method: "POST",
      body: JSON.stringify({ barcode })
    });
  }

  async inventorySummary(): Promise<InventorySummary> {
    return this.request<InventorySummary>("/api/v1/inventory-summary/summary/");
  }

  async listBranches(): Promise<PaginatedResponse<Branch>> {
    return this.request<PaginatedResponse<Branch>>("/api/v1/branches/");
  }

  async listUsers(): Promise<PaginatedResponse<UserListItem>> {
    return this.request<PaginatedResponse<UserListItem>>("/api/v1/users/");
  }

  async listEntities(params: Record<string, string | number | undefined> = {}): Promise<PaginatedResponse<EntityListItem>> {
    return this.request<PaginatedResponse<EntityListItem>>(`/api/v1/entities/${this.query(params)}`);
  }

  async entitySummary(): Promise<EntitySummary> {
    return this.request<EntitySummary>("/api/v1/entities/summary/");
  }

  async getEntity(id: number): Promise<Entity> {
    return this.request<Entity>(`/api/v1/entities/${id}/`);
  }

  async createEntity(input: CreateEntityInput): Promise<Entity> {
    return this.request<Entity>("/api/v1/entities/", {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  async startEntityOnboarding(id: number, workflow_template?: number | null): Promise<EntityOnboarding> {
    return this.request<EntityOnboarding>(`/api/v1/entities/${id}/start-onboarding/`, {
      method: "POST",
      body: JSON.stringify({ workflow_template: workflow_template ?? null, create_activation_ticket: true })
    });
  }

  async completeOnboardingStep(
    entityId: number,
    step_completion: number,
    status: OnboardingStepStatus,
    note = "",
    evidence_label = ""
  ): Promise<EntityOnboarding> {
    return this.request<EntityOnboarding>(`/api/v1/entities/${entityId}/complete-onboarding-step/`, {
      method: "POST",
      body: JSON.stringify({ step_completion, status, note, evidence_label })
    });
  }

  async activateEntity(id: number, note = "Activated after onboarding review."): Promise<Entity> {
    return this.request<Entity>(`/api/v1/entities/${id}/activate/`, {
      method: "POST",
      body: JSON.stringify({ status: "active", note })
    });
  }

  async listOnboardingWorkflowTemplates(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<OnboardingWorkflowTemplate>> {
    return this.request<PaginatedResponse<OnboardingWorkflowTemplate>>(
      `/api/v1/onboarding-workflow-templates/${this.query(params)}`
    );
  }

  async listDocumentAssignments(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<DocumentAssignment>> {
    return this.request<PaginatedResponse<DocumentAssignment>>(`/api/v1/document-assignments/${this.query(params)}`);
  }

  async acknowledgeDocument(id: number, acknowledgement_text = "", evidence_label = ""): Promise<DocumentAssignment> {
    return this.request<DocumentAssignment>(`/api/v1/document-assignments/${id}/acknowledge/`, {
      method: "POST",
      body: JSON.stringify({ acknowledgement_text, evidence_label })
    });
  }

  async signDocument(id: number, acknowledgement_text = "", evidence_label = ""): Promise<DocumentAssignment> {
    return this.request<DocumentAssignment>(`/api/v1/document-assignments/${id}/sign/`, {
      method: "POST",
      body: JSON.stringify({ acknowledgement_text, evidence_label })
    });
  }

  async listConsentRecords(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<ConsentRecord>> {
    return this.request<PaginatedResponse<ConsentRecord>>(`/api/v1/consent-records/${this.query(params)}`);
  }

  async withdrawConsent(id: number): Promise<ConsentRecord> {
    return this.request<ConsentRecord>(`/api/v1/consent-records/${id}/withdraw/`, {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  async listTrainingModules(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<TrainingModule>> {
    return this.request<PaginatedResponse<TrainingModule>>(`/api/v1/training-modules/${this.query(params)}`);
  }

  async listTrainingAssignments(
    params: Record<string, string | number | undefined> = {}
  ): Promise<PaginatedResponse<TrainingAssignment>> {
    return this.request<PaginatedResponse<TrainingAssignment>>(`/api/v1/training-assignments/${this.query(params)}`);
  }

  async complianceSummary(): Promise<ComplianceSummary> {
    return this.request<ComplianceSummary>("/api/v1/training-assignments/summary/");
  }

  async completeTraining(
    id: number,
    input: { completion_note?: string; quiz_score?: number | null; evidence_label?: string }
  ): Promise<TrainingAssignment> {
    return this.request<TrainingAssignment>(`/api/v1/training-assignments/${id}/complete/`, {
      method: "POST",
      body: JSON.stringify(input)
    });
  }

  private async request<T>(
    path: string,
    options: RequestInit & { auth?: boolean } = {}
  ): Promise<T> {
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");

    if (options.auth !== false) {
      const token = this.getToken?.();
      if (token) {
        headers.set("Authorization", `Token ${token}`);
      }
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `Request failed with ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  }

  private query(params: Record<string, string | number | undefined>) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        query.set(key, String(value));
      }
    });
    const rendered = query.toString();
    return rendered ? `?${rendered}` : "";
  }
}

export function createApiClient(baseUrl: string, getToken?: () => string | null | undefined) {
  return new ApiClient(baseUrl.replace(/\/$/, ""), getToken);
}

export const phase2DashboardMetrics: DashboardMetric[] = [
  { label: "Open tickets", value: "0", href: "/tickets", tone: "info" },
  { label: "Payroll pending", value: "0", href: "/payroll-readiness", tone: "warning" },
  { label: "Inventory alerts", value: "0", href: "/inventory", tone: "danger" },
  { label: "Training alerts", value: "0", href: "/training", tone: "warning" },
  { label: "Incidents", value: "0", href: "/incidents", tone: "danger" },
  { label: "AI review", value: "0", href: "/ai-review", tone: "neutral" }
];
