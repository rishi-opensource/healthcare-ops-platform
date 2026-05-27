export const roleLabels = {
  super_admin: "Super Admin",
  manager: "Clinic Manager",
  hr_payroll: "HR / Payroll",
  finance: "Finance",
  compliance: "Compliance",
  receptionist: "Receptionist",
  doctor: "Doctor / Practitioner",
  nurse: "Nurse / Clinical Assistant",
  pharmacist: "Pharmacist",
  inventory: "Inventory / Procurement",
  supplier: "Supplier",
  contractor: "Contractor",
  ai_agent: "AI Agent"
} as const;

export const ticketStatusLabels = {
  draft: "Draft",
  open: "Open",
  in_progress: "In Progress",
  waiting_approval: "Waiting Approval",
  needs_correction: "Needs Correction",
  completed: "Completed",
  closed: "Closed",
  cancelled: "Cancelled"
} as const;

export const statusTone = {
  draft: "neutral",
  open: "info",
  in_progress: "info",
  waiting_approval: "warning",
  needs_correction: "danger",
  completed: "success",
  closed: "neutral",
  cancelled: "neutral"
} as const;

export type RoleCode = keyof typeof roleLabels;
export type TicketStatus = keyof typeof ticketStatusLabels;

