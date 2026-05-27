"use client";

import type {
  Branch,
  CreateTicketInput,
  Ticket,
  TicketCategory,
  TicketListItem,
  TicketPriority,
  TicketStatus,
  TicketSummary,
  UserListItem
} from "@healthcare/api-client";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

const categories: TicketCategory[] = [
  "general",
  "onboarding",
  "patient",
  "appointment",
  "inventory",
  "purchase_order",
  "payroll",
  "leave",
  "incident",
  "contract",
  "supplier",
  "maintenance"
];

const priorities: TicketPriority[] = ["low", "normal", "high", "urgent"];
const statuses: TicketStatus[] = [
  "open",
  "in_progress",
  "waiting_approval",
  "needs_correction",
  "completed",
  "closed",
  "cancelled"
];

function label(value: string) {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function statusTone(status: TicketStatus) {
  if (status === "completed" || status === "closed") return "pill-success";
  if (status === "cancelled") return "pill-danger";
  if (status === "waiting_approval" || status === "needs_correction") return "pill-warning";
  return "pill-info";
}

const emptyTicketForm: CreateTicketInput = {
  title: "",
  description: "",
  category: "general",
  priority: "normal",
  branch: null,
  assigned_to: null,
  source: "web"
};

export default function TicketsPage() {
  const api = useMemo(() => webApiClient(), []);
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [summary, setSummary] = useState<TicketSummary | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [form, setForm] = useState<CreateTicketInput>(emptyTicketForm);
  const [comment, setComment] = useState("");
  const [completionSummary, setCompletionSummary] = useState("");

  async function loadTickets(nextStatus = statusFilter) {
    setLoading(true);
    setMessage("");
    try {
      const [ticketPage, ticketSummary, branchPage, userPage] = await Promise.all([
        api.listTickets(nextStatus ? { status: nextStatus } : {}),
        api.ticketSummary(),
        api.listBranches(),
        api.listUsers()
      ]);
      setTickets(ticketPage.results);
      setSummary(ticketSummary);
      setBranches(branchPage.results);
      setUsers(userPage.results);
      if (!selectedTicket && ticketPage.results[0]) {
        const detail = await api.getTicket(ticketPage.results[0].id);
        setSelectedTicket(detail);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load tickets.");
    } finally {
      setLoading(false);
    }
  }

  async function loadTicket(id: number) {
    setMessage("");
    setSelectedTicket(await api.getTicket(id));
  }

  useEffect(() => {
    void loadTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const created = await api.createTicket({
      ...form,
      branch: form.branch ? Number(form.branch) : null,
      assigned_to: form.assigned_to ? Number(form.assigned_to) : null
    });
    setForm(emptyTicketForm);
    setSelectedTicket(created);
    await loadTickets();
  }

  async function transition(status: TicketStatus) {
    if (!selectedTicket) return;
    try {
      const updated = await api.transitionTicket(selectedTicket.id, status, `Updated from web to ${label(status)}.`);
      setSelectedTicket(updated);
      await loadTickets();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update ticket status.");
    }
  }

  async function assign(value: string) {
    if (!selectedTicket) return;
    const updated = await api.assignTicket(
      selectedTicket.id,
      value ? Number(value) : null,
      "Assignment updated from ticket detail."
    );
    setSelectedTicket(updated);
    await loadTickets();
  }

  async function addComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTicket || !comment.trim()) return;
    await api.addTicketComment(selectedTicket.id, comment.trim(), true);
    setComment("");
    await loadTicket(selectedTicket.id);
  }

  async function complete(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTicket || !completionSummary.trim()) return;
    const updated = await api.completeTicket(selectedTicket.id, {
      completion_summary: completionSummary.trim(),
      outcome: completionSummary.trim(),
      request_approval: true
    });
    setCompletionSummary("");
    setSelectedTicket(updated);
    await loadTickets();
  }

  async function reviewApproval(approvalId: number, status: "approved" | "correction_requested") {
    if (!selectedTicket) return;
    await api.reviewTicketApproval(selectedTicket.id, approvalId, status, label(status));
    await loadTicket(selectedTicket.id);
    await loadTickets();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 3</div>
          <h1 className="title">Universal ticket queue</h1>
          <p className="muted">Create, assign, update, complete, approve, and audit operational tickets.</p>
        </div>
        <select
          className="input compact-input"
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value);
            void loadTickets(event.target.value);
          }}
          aria-label="Filter tickets by status"
        >
          <option value="">All statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {label(status)}
            </option>
          ))}
        </select>
      </div>

      {message ? <div className="alert">{message}</div> : null}

      <section className="grid metric-grid ticket-metrics">
        {summary
          ? [
              ["Open", summary.open],
              ["In progress", summary.in_progress],
              ["Waiting approval", summary.waiting_approval],
              ["Needs correction", summary.needs_correction],
              ["Urgent", summary.urgent],
              ["Assigned to me", summary.assigned_to_me]
            ].map(([name, value]) => (
              <div className="card metric-compact" key={name}>
                <div className="muted">{name}</div>
                <div className="metric-value">{value}</div>
              </div>
            ))
          : null}
      </section>

      <div className="ticket-workspace">
        <section className="card ticket-list-panel">
          <div className="section-title">Queue</div>
          {loading ? <p className="muted">Loading tickets...</p> : null}
          <div className="ticket-list">
            {tickets.map((ticket) => (
              <button
                className={`ticket-row ${selectedTicket?.id === ticket.id ? "ticket-row-active" : ""}`}
                key={ticket.id}
                onClick={() => void loadTicket(ticket.id)}
                type="button"
              >
                <span>
                  <strong>{ticket.ticket_number}</strong>
                  <span>{ticket.title}</span>
                </span>
                <span className={`pill ${statusTone(ticket.status)}`}>{label(ticket.status)}</span>
                <span className="muted">{ticket.assigned_to_email || "Unassigned"}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="card ticket-detail-panel">
          {selectedTicket ? (
            <>
              <div className="detail-heading">
                <div>
                  <div className="eyebrow">{selectedTicket.ticket_number}</div>
                  <h2>{selectedTicket.title}</h2>
                  <p className="muted">{selectedTicket.description || "No description supplied."}</p>
                </div>
                <span className={`pill ${statusTone(selectedTicket.status)}`}>{label(selectedTicket.status)}</span>
              </div>

              <div className="detail-grid">
                <label className="field">
                  <span className="label">Assignee</span>
                  <select
                    className="input"
                    value={selectedTicket.assigned_to || ""}
                    onChange={(event) => void assign(event.target.value)}
                  >
                    <option value="">Unassigned</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.full_name || user.email}
                      </option>
                    ))}
                  </select>
                </label>
                <div>
                  <span className="label">Priority</span>
                  <div>{label(selectedTicket.priority)}</div>
                </div>
                <div>
                  <span className="label">Branch</span>
                  <div>{selectedTicket.branch_name || "No branch"}</div>
                </div>
              </div>

              <div className="button-row">
                {statuses.filter((status) => status !== selectedTicket.status).map((status) => (
                  <button className="button secondary-button" key={status} onClick={() => void transition(status)} type="button">
                    {label(status)}
                  </button>
                ))}
              </div>

              <form className="inline-form" onSubmit={(event) => void complete(event)}>
                <input
                  className="input"
                  value={completionSummary}
                  onChange={(event) => setCompletionSummary(event.target.value)}
                  placeholder="Completion summary"
                />
                <button className="button" type="submit">
                  Complete
                </button>
              </form>

              <div className="detail-columns">
                <div>
                  <div className="section-title">Approvals</div>
                  <div className="stack">
                    {selectedTicket.approvals.map((approval) => (
                      <div className="subcard" key={approval.id}>
                        <div>
                          <strong>{label(approval.approval_type)}</strong>
                          <div className="muted">{label(approval.status)}</div>
                        </div>
                        {approval.status === "pending" ? (
                          <div className="button-row">
                            <button className="button secondary-button" onClick={() => void reviewApproval(approval.id, "approved")} type="button">
                              Approve
                            </button>
                            <button
                              className="button danger-button"
                              onClick={() => void reviewApproval(approval.id, "correction_requested")}
                              type="button"
                            >
                              Correct
                            </button>
                          </div>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="section-title">Timeline</div>
                  <div className="timeline">
                    {selectedTicket.status_history.map((item) => (
                      <div className="timeline-item" key={item.id}>
                        <strong>{label(item.to_status)}</strong>
                        <span className="muted">{item.note || "Status updated"}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <form className="inline-form" onSubmit={(event) => void addComment(event)}>
                <input
                  className="input"
                  value={comment}
                  onChange={(event) => setComment(event.target.value)}
                  placeholder="Add internal note"
                />
                <button className="button" type="submit">
                  Add note
                </button>
              </form>
              <div className="stack">
                {selectedTicket.comments.map((item) => (
                  <div className="subcard" key={item.id}>
                    <strong>{item.author_email || "System"}</strong>
                    <span>{item.body}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="muted">Select a ticket to see details.</p>
          )}
        </section>

        <section className="card ticket-create-panel">
          <div className="section-title">Create ticket</div>
          <form className="form wide-form" onSubmit={(event) => void createTicket(event)}>
            <label className="field">
              <span className="label">Title</span>
              <input
                className="input"
                required
                value={form.title}
                onChange={(event) => setForm({ ...form, title: event.target.value })}
              />
            </label>
            <label className="field">
              <span className="label">Description</span>
              <textarea
                className="input textarea"
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
            </label>
            <label className="field">
              <span className="label">Category</span>
              <select
                className="input"
                value={form.category}
                onChange={(event) => setForm({ ...form, category: event.target.value as TicketCategory })}
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {label(category)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span className="label">Priority</span>
              <select
                className="input"
                value={form.priority}
                onChange={(event) => setForm({ ...form, priority: event.target.value as TicketPriority })}
              >
                {priorities.map((priority) => (
                  <option key={priority} value={priority}>
                    {label(priority)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span className="label">Branch</span>
              <select
                className="input"
                value={form.branch || ""}
                onChange={(event) => setForm({ ...form, branch: event.target.value ? Number(event.target.value) : null })}
              >
                <option value="">No branch</option>
                {branches.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
            </label>
            <button className="button" type="submit">
              Create ticket
            </button>
          </form>
        </section>
      </div>
    </AppShell>
  );
}
