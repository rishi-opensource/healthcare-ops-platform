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
